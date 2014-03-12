import beaglebone_pru_adc as adc
import time

print 'Will start capture, keep it running for 10 seconds, then get timer value'
print 'This is used to compute the capture speed (time value of one timer unit)'
print 'Please wait...'

capture = adc.Capture()

capture.encoder0_pin = 0 # AIN0, aka P9_39
capture.encoder1_pin = 2 # AIN2, aka P9_37
capture.encoder0_threshold = 3000 # you will want to adjust this
capture.encoder1_thredhold = 3000 # and this...
capture.encoder0_delay = 100 # prevents "ringing", adjust if needed
capture.encoder1_delay = 100 # ... same
capture.start()

time.sleep(10)

timer = capture.timer

capture.stop()
capture.wait()
capture.close()

print 'Capture runs at %d readings per second' % (timer // 10)
print 'Time value of one timer unit is %d nanosec' % (1000000000 // timer)
