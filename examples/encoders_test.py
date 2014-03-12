import beaglebone_pru_adc as adc
import contextlib
import time

@contextlib.contextmanager
def init_capture(threshold0, threshold1, delay=0):

	capture = adc.Capture()
	capture.encoder0_pin = 0 # AIN0, aka P9_39
	capture.encoder1_pin = 2 # AIN2, aka P9_37
	capture.encoder0_threshold = threshold0
	capture.encoder1_thredhold = threshold1
	capture.encoder0_delay = delay
	capture.encoder1_delay = delay
	capture.start()

	yield capture

	capture.stop()
	capture.wait()
	capture.close()

with init_capture(2000, 2000, 200) as c:

	enc0_ticks = c.encoder0_values[3]
	enc1_ticks = c.encoder1_values[3]

	while True:
		v0 = c.encoder0_values
		v1 = c.encoder1_values

		if v0[3] != enc0_ticks or v1[3] != enc1_ticks:
			enc0_ticks = v0[3]
			enc1_ticks = v1[3]
			enc0_speed = 10000. / v0[4]
			enc1_speed = 10000. / v1[4]

			print '%8d[%4.2lf] %8d[%4.2lf]' % (enc0_ticks, enc0_speed, enc1_ticks, enc1_speed)

		time.sleep(0.001)
