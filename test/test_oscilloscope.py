import beaglebone_pru_adc as adc
import time
import mmap
import struct

capture = adc.Capture()

capture.oscilloscope_init(4, 10)

capture.start()

time.sleep(1.0)

capture.stop()
capture.wait()

print 'timer:', capture.timer
print 'ema_pow:', capture.ema_pow
print 'values:', capture.values
print 'enc pins:', capture.encoder0_pin, capture.encoder1_pin
print 'encoder0_values:', capture.encoder0_values
print 'encoder1_values:', capture.encoder1_values

print 'encoder0_threshold:', capture.encoder0_threshold
print 'encoder1_threshold:', capture.encoder1_threshold

for x in capture.oscilloscope_data(10):
	print x

capture.close()
