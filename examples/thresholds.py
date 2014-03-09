import beaglebone_pru_adc as adc
import time

capture = adc.Capture()
capture.encoder0_pin = 0 # AIN0
capture.encoder1_pin = 2 # AIN2

# set threshold such that encoders never fire any ticks
capture.encoder0_threshold=4096
capture.encoder1_threshold=4096

capture.start()

print 'Now you have 10 seconds to rotate each wheel...'
time.sleep(10)

capture.stop()
capture.wait()

_, min0, max0, _, _ = capture.encoder0_values
_, min1, max1, _, _ = capture.encoder1_values

capture.close()

print 'Range for the Encoder0:', min0, '-', max0
print 'Recommended threshold value for encoder 0 is:', int(0.9*(max0-min0))

print 'Range for the Encoder1:', min1, '-', max1
print 'Recommended threshold value for encoder 1 is:', int(0.9*(max1-min1))
