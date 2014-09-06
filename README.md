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

4. User can configure `cap_delay` parameter to run at lower capture speed than the maximum. Capture delay introduces some delay at every capture cycle resulting in speed slowdown. This allows one to configure ADC capture frequency.

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

[examples/basic.py](https://github.com/pgmmpk/beaglebone_pru_adc/tree/master/examples/basic.py)
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

## Slowing down capture speed
[examples/speed_control.py](https://github.com/pgmmpk/beaglebone_pru_adc/tree/master/examples/speed_control.py)
```python
import beaglebone_pru_adc as adc

capture = adc.Capture()

# the bigger the delay the slower capture is
capture.cap_delay = 2000
...

capture.start()
...
```


## Using encoders

[examples/encoders.py](https://github.com/pgmmpk/beaglebone_pru_adc/tree/master/examples/encoders.py)
```python
import beaglebone_pru_adc as adc

capture = adc.Capture()
capture.encoder0_pin = 0 # AIN0, aka P9_39
capture.encoder1_pin = 2 # AIN2, aka P9_37
capture.encoder0_threshold = 3000 # you will want to adjust this
capture.encoder1_thredhold = 3000 # and this...	
capture.encoder0_delay = 100 # prevents "ringing", adjust if needed
capture.encoder1_delay = 100 # ... same
capture.start()

for _ in range(1000):
	print capture.timer, capture.encoder0_values, capture.encoder1_values

capture.stop()
capture.wait()
capture.close()
```

## Advanced: oscilloscope mode

[examples/oscilloscope.py](https://github.com/pgmmpk/beaglebone_pru_adc/tree/master/examples/oscilloscope.py)
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

## Choosing encoder threshold
Life is random and no two encoders are the same. Therefore, to get the best out of your wheel
encoder you need to adjust the threshold. Here is a simple method for doing this:

* Configure encoder pins
* Set encoder threshold to a very high number (e.g. any number higher than 4095 will guarantee that encoder tick will never fire)
* Start capture
* Rotate each wheel few times while capturing
* Examine encoder values. We are interested in min/max pair for each encoder. It will tell us what the actual signal range is for each
wheel encoder
* Choose threshold which is 5-10% lower than the range seen.

Here is the code that does it (except for the wheel rotation which need to be done manually):

[examples/thresholds.py](https://github.com/pgmmpk/beaglebone_pru_adc/tree/master/examples/thresholds.py)

```python
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
print 'Recommended threshold value for encoder 1 is:', int(0.9*(max1-min1))``` 
```
## Choosing encoder delay

Encoders seem to be not very sensitive to this value. Try `100` that may work just fine for you.

`delay` supresses noise and prevents it from registering a tick. When `delay` is zero, Schmitt software filtering works in a standard way:
whenever signal exceeds `min+threshold` uptick is registered, and whenever signal becomes less than `max-threshold` a downtick is registered.

With non-zero `delay` we require signal to overcome threshold for that many consequtive readings. Therefore, small random peaks are just ignored.

If you make `delay` too low, you may suffer spurious ticks triggered by signal noise. If you make it too high, and your robot goes very fast,
you risk genuine tick to be considered a "noise" and hence ignored. Typical period of a tick for fast-moving wheels is around 1000 time units
(reminder: time unit is one ADC read operation). Therefore, `delay` values of up to 250 seem still reasonable.



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

### Capture.encoder0_delay, Capture.encoder1_delay

Delay value to filter out noise. Default value is `0` (no filtering). Reasonable value is `100` which requires signal to stay high
for 100 timer units before uptick is registered, and stay low for 100 timer units before downtick is registered.

### Capture.encoder0_values, Capture.encoder1_values
Read-only property that returns a 5-tuple describing the state of the encoder. Values are: (raw, min, max, ticks, speed).

* `raw` is the latest raw value for the encoder pin (for internal use and debugging)
* `min` is the minimum value seen during the current tick window (for internal use and debugging)
* `max` is the maximum value seen during the current tick window (for internal use and debugging)
* `ticks` is the number of encoder ticks seen since the start of the driver. Ticks are counted on the falling edge of the signal.
   This value can also be retrieved with a helper property `encoder0_ticks`, `encoder1_ticks`. 
* `speed` is the width of the last encoder tick in `timer` units. Its inverse provides a measure of speed.
	This value can also be retrieved with `encoder0_speed`, `encoder1_speed`

### Capture.encoder0_ticks, Capture.encoder1_ticks
Read-only property that returns number of ticks registered for the corresponding encoder.
Same value is returned as 4-th element of tuple retrieved by `encoder0_values`, `encoder1_values`. 


### Capture.encoder0_speed, Capture.encoder1_speed
Read-only property that returns inverse speed of the last registered tick.
Same value is returned as 5-th element of tuple retrieved by `encoder0_values`, `encoder1_values`.

Note that name is a misnomer. Bigger values mean smaller speed. Actual speed of rotation for 16-teeth encoder can be
computed as 
```
radians_per_sec = (PI / 8) * 122000 / encoder_speed
``` 
Here PI/8 is the 1/16 of a circle - how many radians one tick represents, 122000 is (approximate) capture speed,
and encoder_speed is teh value returned by the driver (which is the width in timer units of the tick).

### Capture.cap_delay
Extra delay to be introduced in the main capture loop for the purpose of slowing down the capture speed. Default value is 0, which means "no delay". Play with the code in `examples/speed_control.py` to choose the correct delay value for the desired speed. Try values of 100, 1000, 10000 to see the difference.

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
	
	For the complete list of local memory variables and their offset values see
	[src/firmware.h](https://github.com/pgmmpk/beaglebone_pru_adc/blob/master/src/firmware.h) and 
	[src/README.md](https://github.com/pgmmpk/beaglebone_pru_adc/blob/master/src/README.md).

* `numsamples` - number of samples to record. This is limited by the size of the DDR memory allocated to the `uio_pruss` device driver. It
	is typically 0x40000, which allows recording of up to 64K oscilloscope values. This amounts to about 0.5 sec in time units.

### Capture.oscilloscope_is_complete()
Returns `True` if capture was finished (i.e. the required number of samples was recorded and is ready for retrieval).

### Capture.oscilloscope_data(numsamples)
Retrieves `numsamples` of data from driver DDR memory. Before calling this its a good idea to verify that oscilloscope indeed
finished capturing all samples by calling `oscilloscope_is_complete()` (or you might read some garbage from not yet initialized memory).
Of course, `numsamples` should be the same value as used in `oscilloscope._init()`.

Returns an array of integers representing time evolution of the value of interest as determined by `offset` in `oscilloscope_init()` call.

## Resources

1. [AM335x Technical Reference Manual](http://www.phytec.com/wiki/images/7/72/AM335x_techincal_reference_manual.pdf). Older revision where PRU section is not deleted is [here](http://elinux.org/images/6/65/Spruh73c.pdf).
2. [How to control ADC (see comments by Lenny and Abd)](http://beaglebone.cameon.net/home/reading-the-analog-inputs-adc)
3. Hipstercircuits blog and [this](http://hipstercircuits.com/beaglebone-pru-ddr-memory-access-the-right-way) post in particular (how to communicate with DDR memory).
4. Excellent [PyPRUSS](https://bitbucket.org/intelligentagent/pypruss) library.
6. [prussdrv.c source](https://github.com/beagleboard/am335x_pru_package/blob/master/pru_sw/app_loader/interface/prussdrv.c) by Texas Instruments.
7. [PRU assembly reference](http://processors.wiki.ti.com/index.php/PRU_Assembly_Instructions).
8. [PRU docs on TI wiki](http://processors.wiki.ti.com/index.php/Programmable_Realtime_Unit_Subsystem). Includes [list of Open Source PRU projects](http://processors.wiki.ti.com/index.php/PRU_Projects).
9. [Derek Molloy's BeagleBone website](http://derekmolloy.ie/beaglebone/).
10. [Ultrasound sensors with PRU](https://github.com/Teknoman117/beaglebot) by Teknoman.


## License
MIT
