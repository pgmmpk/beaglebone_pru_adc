import _pru_adc
import glob
import re
import os

SLOTS = glob.glob('/sys/devices/bone_capemgr.*/slots')[0]

def _is_pru_loaded():
	with open(SLOTS, 'r') as f:
		for line in f:
			if re.search(r'BB-BONE-PRU-01', line):
				return True

	return False

def _is_adc_loaded():
	with open(SLOTS, 'r') as f:
		for line in f:
			if re.search(r'BB-ADC', line):
				return True

	return False

def _ensure_pru_loaded():
	if _is_pru_loaded():
		return

	with open(SLOTS, 'w') as f:
		f.write('BB-BONE-PRU-01')

def _ensure_adc_loaded():
	if _is_adc_loaded():
		return

	with open(SLOTS, 'w') as f:
		f.write('BB-ADC')

_ensure_pru_loaded()
_ensure_adc_loaded()

class Capture(_pru_adc.Capture):

	def start(self):
		firmware = os.path.dirname(__file__) + '/firmware/firmware.bin'
		print firmware
		_pru_adc.Capture.start(self, firmware)
