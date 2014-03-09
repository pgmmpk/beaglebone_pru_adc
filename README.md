# beaglebone_pru_adc

Fast analog sensor capture for [Beaglebone Black](http://beaglebone.org).

## Introduction

Beaglebone Black processor has built-in ADC unit, that is technically called "Touchscreen/ADC subsystem" in documentation.
It can be used to capture analog signals and digitize them. Unit supports up to 8 inputs. (Incidentally, there
is just a single ADC chip and capture from 8 inputs happens sequentially by multiplexing pins. This means that
capturing a single pin is faster than capturing several pins.)

Another cool feature of BBB processor is that it has two "Programmable Real-time Units", or PRUs. These are
just two small RISC processors that run at 200Mhz independently from the main CPU. They have access to everything
on the board.

## What is it?
This is a Python module that captures ADC signals by utilizing PRU. The capture is very fast, because it happens
in parallel to the main CPU work. User can query signals at any time. This is as fast as a memory read operation.

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

Assume Angstrom distribution with kernel 3.8.13:
```bash
# uname -a
Linux beaglebone 3.8.13 #1 SMP Wed Sep 4 09:09:32 CEST 2013 armv7l GNU/Linux
```

```bash
# cat /etc/angstrom-version 
Angstrom v2012.12 (Core edition)
Built from branch: angstrom-staging-yocto1.3
Revision: 2ac8ed60f1c4152577f334b223b9203f57ed1722
Target system: arm-angstrom-linux-gnueabi
```

1. Install pre-requisites:
	```bash
	opkg update && opkg install python-pip python-setuptools python-smbus
	```

2. Clone GIT repository
	```bash
	git clone https://github.com/pgmmpk/beaglebone_pru_adc.git
	```
	
	Note: if GIT refuses to clone, this might help (warning: disabling GIT SSL verification may pose a security risk)
	```bash
	git config --global http.sslVerify false
	```

3. Build and install python package
	```bash
	cd beaglebone_pru_adc

	python setup.py install
	```

4. See it working
	```bash
	python examples/basic.py
	```

## Basic usage

[examples/basic.py](https://github.com/pgmmpk/beaglebone_pru_adc/examples/basic.py)
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

[examples/encoders.py](https://github.com/pgmmpk/beaglebone_pru_adc/examples/encoders.py)
```python
import beaglebone_pru_adc as adc

capture = adc.Capture()
capture.encoder0_pin = 0 # AIN0, aka P9_39
capture.encoder1_pin = 2 # AIN2, aka P9_37
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

[examples/oscilloscope.py](https://github.com/pgmmpk/beaglebone_pru_adc/examples/oscilloscope.py)
```python
import beaglebone_pru_adc as adc
import time

numsamples = 10000 # how many samples to capture

capture = adc.Capture()

capture.oscilloscope_init(adc.OFF_VALUES, numsamples) # captures AIN0 - the first elt in AIN array
#capture.oscilloscope_init(adc.OFF_VALUES+8, numsamples) # captures AIN2 - the third elt in AIN array
capture.start()

for _ in range(10):
	if capture.oscilloscope_is_complete():
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
ADC input pins are named AIN0-AIN7 (there are 8 of them). They are located on P9 header and mapped to the header pins as follows:
```
AIN0: P9_39
AIN1: P9_40
AIN2: P9_37
AIN3: P9_38
AIN4: P9_35
AIN5: P9_36
AIN6: P9_33
AIN7: ?????
```
Digital capture produces an integer in the range 0-4095 (inclusively) for each analog input.

Driver lifetime is

* `Capture` object is constructed
* Optionally configure driver by setting properties
* `Capture.start()` - driver started
* Main processing is happening here. Read IR and encoder values
* `Capture.stop()` - request sent to the driver to stop capturing and exit
* `Capture.wait()` - wait for driver exit
* `Capture.close()` - releases all resources

Methods and properties of `Capture` object:

### Capture.start()
Starts capture driver.

### Capture.stop()
Sets flag signaling driver to exit exit capture loop and halt.

### Capture.wait()
Blocks caller until driver halts.

### Capture.close()
Releases all driver resources.

### Capture.timer
Read-only property. Contains the number of ADC reads since the start of the driver.

### Capture.ema_pow
EMA smoothening factor. Smoothening is performed according to the formula:
```
ema += (value - ema / 2^ema_pow)
```
Therefore, `2^ema_pow` gives the smoothening size. 

Valid range: 0-31

Default value is `ema_pow=0` which degenerates to no smoothening.

### Capture.values
Read-only properties. Returns the tuple of 8 ADC pin values: (AIN0, AIN1, AIN2, AIN3, AIN4, AIN5, AIN6, AIN7). 

If EMA smoothening
was set, these values will represent the result of EMA filtering. Note that due to the way driver applies the EMA smoothening, the values will
be scaled up. To bring them back into the 0-4095 range, divide them by `2^ema_pow` (or shift values right by `ema_pow` bits).

If some pins were declared as encoder pins, the corresponding slots in the tuple will stay zero. Use `Capture.encoder0_values`
and `Capture.encoder1_values` to read encoder pin values.

### Capture.encoder0_pin, Capture.encoder1_pin
Setting this property to value in range 0-7 enables corresponding encoder and makes it use this pin. 
Setting it to any other value disables corresponding encoder.

Default value is `0xff` (disabled).

### Capture.encoder0_threshold, Capture.encoder1_threshold

Threshold value for Schmitt filtering of encoder. Setting this value too high will have an effect of encoder never producing any ticks.
Setting it too low opens possibility of spurious ticks triggered by random analog noise.

### Capture.encoder0_values, Capture.encoder1_values
Read-only property that returns a 5-tuple describing the state of the encoder. Values are: (raw, min, max, ticks, speed).

* `raw` is the latest raw value for the encoder pin (for internal use and debugging)
* `min` is the minimum value seen during the current tick window (for internal use and debugging)
* `max` is the maximum value seen during the current tick window (for internal use and debugging)
* `ticks` is the number of encoder ticks seen since the start of the driver. Ticks are counted on the falling edge of the signal.
* `speed` is the width of the last encoder tick in `timer` units. Its inverse provides a measure of speed.

### Capture.oscilloscope_init(offset, numsamples)
Sets up driver for "oscilloscope" mode. In this mode on every ADC capture a value from driver local memory will be written
out to a memory buffer. The content of this buffer can later be analyzed (e.g. written to a CSV file and plotted out).

Parameters:

* `offset` - offset into local memory where the value of interest is located. Some important offsets are:
	* `OFF_VALUES` - offset to the beginning of AIN values array. Use `OFF_VALUES` to examine AIN0, `OFF_VALUES+4` to examine
		AIN1, etc.
	* `OFF_ENC0_VALUES` - offset to the beginning of encoder0 values. Use `OFF_ENC0_VALUES` to examine raw value of encoder0,
		use `OFF_ENC0_VALUES+4` to examine `max` variable of encoder0, etc.
	* `OFF_ENC1_VALUES` - offset to the beginning of encoder1 values.
	
	For the complete list of local memory variables and their offset values see [src/firmware.h' and [src/READEM.md].

* `numsamples` - number of samples to record. This is limited by the size of the DDR memory allocated to the `uio_pruss` device driver. It
	is typically 0x40000, which allows recording of up to 64K oscilloscope values. This amounts to about 0.5 sec in time units.

### Capture.oscilloscope_is_complete()
Returns `True` if capture was finished (i.e. the required number of samples was recorded and is ready for retrieval).

### Capture.oscilloscope.data(numsamples)
Retrieves `numsamples` of data from driver DDR memory. Before calling this its a good idea to verify that oscilloscope indeed
finished capturing all samples by calling `oscilloscope_is_complete()` (or you might read some garbage from not yet initialized memory).
Of course, `numsamples` should be the same value as used in `oscilloscope._init()`.

Returns an array of integers representing time evolution of the value of interest as determined by `offset` in `oscilloscope_init()` call.

## License
MIT
