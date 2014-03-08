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

	{% highlight bash %}
	opkg update && opkg install python-pip python-setuptools python-smbus
	python setup.py install
	{% endhighlight %}

## License
MIT
