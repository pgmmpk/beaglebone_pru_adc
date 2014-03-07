import beaglebone_pru_adc as adc
import time
import mmap
import struct
import pypruss

pypruss.init()							# Init the PRU
pypruss.open(0)							# Open PRU event 0 which is PRU0_ARM_INTERRUPT
pypruss.pruintc_init()					# Init the interrupt controller

with open("/dev/uio0", 'r+b') as f1:
	pru0_mem = mmap.mmap(f1.fileno(), 0x200, offset=0)

#capture = adc.Capture()

#capture.start()

pypruss.exec_program(0, "beaglebone_pru_adc/firmware/firmware.bin")		# Load firmware "t.bin" on PRU 0

time.sleep(1.0)
struct.pack_into('L', pru0_mem, 0x0008, 1) # exit flag

pypruss.wait_for_event(0)				# Wait for event 0 which is connected to PRU0_ARM_INTERRUPT
pypruss.clear_event(0)					# Clear the event

time.sleep(0.5)

capture.stop()

for off in range(0, 0x81, 4):
	read_back = struct.unpack("L", pru0_mem[off:off+4])[0]
	print hex(off), ':', hex(read_back)

capture.wait()

capture.close()