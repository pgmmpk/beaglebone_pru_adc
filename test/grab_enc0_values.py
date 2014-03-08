import beaglebone_pru_adc as adc
import time
import mmap
import struct

numsamples = 64000

capture = adc.Capture()

capture.oscilloscope_capture_init(capture.OFF_VALUES, numsamples)

capture.start()

print 'Oscilloscope capture started'
while not capture.oscilloscope_capture_complete():
	print '...'
	time.sleep(0.2)

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

with open('data.csv', 'w') as f:
	for x in capture.oscilloscope_capture_data(numsamples):
		f.write(str(x) + '\n')
print 'File "data.csv" saved, exiting'

capture.close()
