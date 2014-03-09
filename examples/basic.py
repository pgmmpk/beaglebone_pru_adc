import beaglebone_pru_adc as adc

capture = adc.Capture()

capture.start()

for _ in range(1000):
    print capture.timer, capture.values

capture.stop() # ask driver to stop
capture.wait() # wait for graceful exit
capture.close()
