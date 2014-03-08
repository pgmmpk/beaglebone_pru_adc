import beaglebone_pru_adc as adc
import time
import mmap
import struct

with open("/dev/uio0", 'r+b') as f1:
	pru0_mem = mmap.mmap(f1.fileno(), 0x200, offset=0)

capture = adc.Capture()

capture.start()

time.sleep(1.0)
capture.stop()

for off in range(0, 0x81, 4):
	read_back = struct.unpack("L", pru0_mem[off:off+4])[0]
	print hex(off), ':', hex(read_back)

capture.wait()

capture.close()
