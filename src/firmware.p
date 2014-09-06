// (C) 2014 Mike Kroutikov

#define PRU0_ARM_INTERRUPT 19

#define ADC_BASE 0x44e0d000

#define CONTROL 0x0040
#define SPEED   0x004c
#define STEP1   0x0064
#define DELAY1  0x0068
#define STATUS  0x0044
#define STEPCONFIG  0x0054
#define FIFO0COUNT  0x00e4

#define ADC_FIFO0DATA   (ADC_BASE + 0x0100)

// Register allocations
#define adc_  r6
#define fifo0data r7
#define out_buff  r8
#define locals r9

#define value r10
#define channel   r11
#define ema   r12
#define encoders  r13
#define cap_delay r14

#define tmp0  r1
#define tmp1  r2
#define tmp2  r3
#define tmp3  r4
#define tmp4  r5

.origin 0
.entrypoint START

START:
	LBCO r0, C4, 4, 4					// Load Bytes Constant Offset (?)
	CLR  r0, r0, 4						// Clear bit 4 in reg 0
	SBCO r0, C4, 4, 4					// Store Bytes Constant Offset

	MOV adc_, ADC_BASE
	MOV fifo0data, ADC_FIFO0DATA
	MOV locals, 0

	LBBO tmp0, locals, 0, 4				// check eyecatcher
	MOV tmp1, 0xbeef1965				//
	QBNE QUIT, tmp0, tmp1				// bail out if does not match

	LBBO out_buff, locals, 0x0c, 4
	LBBO ema, locals, 0x1c, 4
	LBBO encoders, locals, 0x40, 4

	// Read CAP_DELAY value into the register for convenience
	LBBO cap_delay, locals, 0xc4, 4
	
	// Disable ADC
	LBBO tmp0, adc_, CONTROL, 4
	MOV  tmp1, 0x1
	NOT  tmp1, tmp1
	AND  tmp0, tmp0, tmp1
	SBBO tmp0, adc_, CONTROL, 4
	
	// Put ADC capture to its full speed
	MOV tmp0, 0
	SBBO tmp0, adc_, SPEED, 4

	// Configure STEPCONFIG registers for all 8 channels
MOV tmp0, STEP1
	MOV tmp1, 0
	MOV tmp2, 0

FILL_STEPS:
	LSL tmp3, tmp1, 19
	SBBO tmp3, adc_, tmp0, 4
	ADD tmp0, tmp0, 4
	SBBO tmp2, adc_, tmp0, 4
	ADD tmp1, tmp1, 1
	ADD tmp0, tmp0, 4
	QBNE FILL_STEPS, tmp1, 8

	// Enable ADC with the desired mode (make STEPCONFIG registers writable, use tags, enable)
	LBBO tmp0, adc_, CONTROL, 4
	OR   tmp0, tmp0, 0x7
	SBBO tmp0, adc_, CONTROL, 4
	
CAPTURE:
	// check if we need to delay our main loop (to control capture frequency)
	QBNE CAPTURE_DELAY, cap_delay, 0
NO_DELAY:
	
	MOV tmp0, 0x1fe	
	SBBO tmp0, adc_, STEPCONFIG, 4   // write STEPCONFIG register (this triggers capture)

	// check for exit flag
	LBBO tmp0, locals, 0x08, 4   // read runtime flags
	QBNE QUIT, tmp0.b0, 0

	
	// check for oscilloscope mode
	LBBO tmp0, locals, 0x14, 4
	QBEQ NO_SCOPE, tmp0, 0
	
	SUB tmp0, tmp0, 4
	SBBO tmp0, locals, 0x14, 4
	LBBO tmp0, locals, 0x10, 4
	LBBO tmp0, locals, tmp0, 4
	SBBO tmp0, out_buff, 0, 4
	ADD out_buff, out_buff, 4

NO_SCOPE:

// increment ticks
	LBBO tmp0, locals, 0x04, 4
	ADD  tmp0, tmp0, 1
	SBBO tmp0, locals, 0x04, 4
	
	// increment encoder ticks
	LBBO tmp0, locals, 0x58, 8
	ADD  tmp1, tmp1, 1
	MAX  tmp0, tmp1, tmp0
	SBBO tmp0, locals, 0x58, 8

	LBBO tmp0, locals, 0x98, 8
	ADD  tmp1, tmp1, 1
	MAX  tmp0, tmp1, tmp0
	SBBO tmp0, locals, 0x98, 8
	SBBO tmp0, locals, 0x98, 8

WAIT_FOR_FIFO0:
	LBBO tmp0, adc_, FIFO0COUNT, 4
	QBNE WAIT_FOR_FIFO0, tmp0, 8

READ_ALL_FIFO0:  // lets read all fifo content and dispatch depending on pin type
	LBBO value, fifo0data, 0, 4
	LSR  channel, value, 16
	AND channel, channel, 0xf
	MOV tmp1, 0xfff
	AND value, value, tmp1

	// here we have true captured value and channel
	QBNE NOT_ENC0, encoders.b0, channel
	MOV channel, 0
	CALL PROCESS
	JMP NEXT_CHANNEL

NOT_ENC0:
	QBNE NOT_ENC1, encoders.b1, channel
	MOV channel, 1
	CALL PROCESS
	JMP NEXT_CHANNEL

NOT_ENC1:
	LSL tmp1, channel, 2   // to byte offset
	ADD tmp1, tmp1, 0x20   // base of the EMA values
	LBBO tmp2, locals, tmp1, 4
	LSR tmp3, tmp2, ema
	SUB tmp3, value, tmp3
	ADD tmp2, tmp2, tmp3
	SBBO tmp2, locals, tmp1, 4

NEXT_CHANNEL:
	SUB tmp0, tmp0, 1
	QBNE READ_ALL_FIFO0, tmp0, 0

JMP CAPTURE

QUIT:
	MOV R31.b0, PRU0_ARM_INTERRUPT+16   // Send notification to Host for program completion
	HALT

CAPTURE_DELAY:
	MOV tmp0, cap_delay
DELAY_LOOP:
	SUB tmp0, tmp0, 1
	QBNE DELAY_LOOP, tmp0, 0
	JMP NO_DELAY

PROCESS:                                // lets process wheel encoder value
	LSL channel, channel, 6
	ADD channel, channel, 0x44
	LBBO &tmp1, locals, channel, 16     // load tmp1-tmp4 (threshold, raw, min, max)
	MOV tmp2, value
	MIN tmp3, tmp3, value
	MAX tmp4, tmp4, value
	SBBO &tmp1, locals, channel, 16     // store min/max etc
	ADD tmp2, tmp3, tmp1                // tmp2 = min + threshold
	QBLT MAYBE_TOHIGH, value, tmp2
	ADD tmp2, value, tmp1               // tmp2 = value + threshold
	QBLT MAYBE_TOLOW, tmp4, tmp2

	// zero out delays
	ADD channel, channel, 32
	MOV tmp1, 0
	MOV tmp2, 0
	SBBO &tmp1, locals, channel, 8

	RET

MAYBE_TOHIGH:
	ADD channel, channel, 28
	LBBO &tmp1, locals, channel, 12 // load tmp1-tmp3 with (delay, up_count, down_count)
	ADD tmp2, tmp2, 1               // up_count++
	MOV tmp3, 0                     // down_count=0
	SBBO &tmp1, locals, channel, 12
	QBLT TOHIGH, tmp2, tmp1
	
	RET

MAYBE_TOLOW:
	ADD channel, channel, 28
	LBBO &tmp1, locals, channel, 12 // load tmp1-tmp3 with (delay, up_count, down_count)
	ADD tmp3, tmp3, 1               // down_count++
	MOV tmp2, 0                     // up_count=0
	SBBO &tmp1, locals, channel, 12
	QBLT TOLOW, tmp3, tmp1
	
	RET

TOLOW:
	MOV tmp3, 0
	MOV tmp2, 0
	SBBO &tmp1, locals, channel, 12  // up_count = down_count = 0
	
	SUB channel, channel, 20
	MOV tmp2, value                  // min = max = value
	MOV tmp3, value
	SBBO &tmp2, locals, channel, 8
	
	ADD channel, channel, 8
	LBBO &tmp2, locals, channel, 12  // ticks, speed, acc
	ADD tmp2, tmp2, 1                // ticks++
	MOV tmp3, tmp4                   // speed = acc
	MOV tmp4, 0                      // acc = 0
	SBBO &tmp2, locals, channel, 12
	RET
	
TOHIGH:
	MOV tmp3, 0
	MOV tmp2, 0
	SBBO &tmp1, locals, channel, 12  // up_count=0, down_count=0

	SUB channel, channel, 20
	MOV tmp2, value                  // min = max = value
	MOV tmp3, value
	SBBO &tmp2, locals, channel, 8
	RET

