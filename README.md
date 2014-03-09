# beaglebone_pru_adc

Fast analog sensor capture for Beaglebone Black

## Introduction

BeagleBoard Black has built-in ADC unit, that is technically called "Touchscreen/ADC subsystem" in documentation.
It can be used to capture analog signals and digitize them. Unit supports up to 8 inputs. Internally, there
is just a single ADC chip and capture from 8 inputs happens sequentially by multiplexing pins. This means that
capturing a single pin is faster than capturing several pins.

Another cool feature of BBB processor is that it has two "Programmable Real-time Units", or PRUs. These are
just two small RISC processors that run at 200Mhz independently from the main CPU. They have access to everything
on the board.

## What is it?
This is a Python module that captures ADC signals by utilizing PRU. The capture is very fast, because it happens
in parallel to main CPU work. User can query signals at any time. This is as fast as a memory read operation.

In addition to just presenting the current ADC values to the user, this driver can perform some useful data
processing:

1. It can apply EMA-filtering (Exponential moving average) with pre-configured smoothing factor. This is useful
for smoothening noisy signals (e.g. IR sensors).

2. Up to two inputs can be configured as "wheel encoders". Then driver will not do any EMA filtering, but
instead apply Schmitt-filtering to these signals and compute ticks and distance between encoder ticks (which 
is a measure of wheel speed).

3. Driver can be configured to perform "oscilloscope capture", i.e. capture any of the computed value in real time
and store the result in memory for subsequent analysis. This is useful for researching analog input shape and tuning
smoothing parameters and Schmitt filter threshold.

## Installation

Assume Angstrom distribution.

Install pre-requisites:
```bash
opkg update && opkg install python-pip python-setuptools python-smbus
```

Clone GIT repository

```bash
git config --global http.sslVerify false

git clone https://github.com/pgmmpk/beaglebone_pru_adc.git
```

Install
```bash
python setup.py install
```

## Basic usage
```python
import beaglebone_pru_adc as adc

capture = adc.Capture()

capture.start()

for _ in range(1000):
	print capture.timer, capture.values

capture.stop()
capture.wait()
capture.close()
```

## Using encoders
```python
import beaglebone_pru_adc as adc

capture = adc.Capture()
capture.encoder0_pin = 0 # AIN0, aka P8_39
capture.encoder1_pin = 2 # AIN2, aka P8_37
capture.encoder0_threshold = 3000 # you will want to adjust this
capture.encoder1_thredhold = 3000 # and this...	
capture.start()

for _ in range(1000):
	print capture.timer, capture.encoder0_values, capture.encoder1_values

capture.stop()
capture.wait()
capture.close()
```

## Advanced: oscilloscope mode
```python
import beaglebone_pru_adc as adc
import time

numsamples = 10000 # how many samples to capture

capture = adc.Capture()

capture.oscilloscope_capture_init(adc.OFF_VALUES, numsamples) # captures AIN0 - the first elt in AIN array
#capture.oscilloscope_capture_init(adc.OFF_VALUES+8, numsamples) # captures AIN2 - the third elt in AIN array
capture.start()

for _ in range(10):
	if capture.oscilloscope_capture.complete():
		break
	print '.'
	time.sleep(0.1)

capture.stop()
capture.wait()

print 'Saving oscilloscope values to "data.csv"'

with open('data.csv', 'w') as f:
	for x in capture.oscilloscope_data(numsamples):
		f.write(str(x) + '\n')

print 'done'

capture.close()
```


## Reference
TODO


## License
MIT
