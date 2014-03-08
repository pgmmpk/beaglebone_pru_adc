PASM = ../pypruss/PASM/pasm

all:
	$(PASM) -b src/firmware.p beaglebone_pru_adc/firmware/firmware
	#python setup.py build_ext --inplace
