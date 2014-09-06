#ifndef _FIRMWARE_H
#define _FIRMWARE_H

typedef unsigned int word;
typedef unsigned short halfword;
typedef unsigned char byte;

typedef struct {
	word threshold;				// threshold used for detecting wheel encoder ticks
	word raw;					// raw value of encoder
	word min;					// min value for current half-tick
	word max;					// max value for current half-tick
	word ticks;					// count of encoder ticks
	word speed;					// width of last encoder tick in "timer" units, aka inverse speed
#define INITIAL_ACC_VAL (0x7fffffff)
	word acc;					// work area for speed computation
	word delay;					// activation delay, in timer units.
	word uptick_time;			// work area for computing uptick delay
	word downtick_time;			// work area for computing downtick delay
	word reserved[6];
} enc_local_t;

/*
 * Local memory of the firmware
 */
typedef struct {
#define EYECATCHER (0xbeef1965)
	word eyecatcher;			// eyecacher (for sanity checks)
	word timer;					// timer: counts number of ADC reads
	word flags;					// runtime flags. write 1 to exit capture loop
	
	struct {
		word addr;				// address of DDR memory bank
		word offset;			// byte offset into local memory to capture for `scope mode
		word length;			// byte size of available DDR mem bank (non-zero triggers `scope capture)
	} scope;
	
	word reserved0;
	
	word ema_pow;				// exponent for EMA averaging: ema += (value - ema/2^ema_pow)
	
	word ain_ema[8];			// captured and EMA-averaged values of all 8 ADC pins
	
	struct {
		byte encoder0;			// pin number of first wheel encoder ENC0 (0-7)
		byte encoder1;			// pin number of second wheel encoder ENC1 (0-7)
		byte reserved[2];
	} enc;
	
	enc_local_t enc_local[2];	// local work memory for each wheel encoder
	word cap_delay;				// extra delay to control capture frequency
	
} locals_t;

#endif
