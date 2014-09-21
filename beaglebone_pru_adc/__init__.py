import _pru_adc
import glob
import re
import os
import mmap
import struct
import time
import array


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
	time.sleep(0.2) # let things settle before using this driver

def _ensure_adc_loaded():
	if _is_adc_loaded():
		return
    
	with open(SLOTS, 'w') as f:
		f.write('BB-ADC')
	time.sleep(0.2) # let things settle before using this driver

_ensure_pru_loaded()
_ensure_adc_loaded()

# Useful offsets from firmware.h
OFF_FLAG        = 0x0008
OFF_TIMER       = 0x0004
OFF_EMA_POW     = 0x001c
OFF_VALUES      = 0x0020
OFF_ENC0_PIN    = 0x0040
OFF_ENC1_PIN    = 0x0041
OFF_ENC0_THRESH = 0x0044
OFF_ENC1_THRESH = 0x0084
OFF_ENC0_VALUES = 0x0048
OFF_ENC1_VALUES = 0x0088
OFF_ENC0_TICKS  = 0x0054
OFF_ENC1_TICKS  = 0x0094
OFF_ENC0_SPEED  = 0x0058
OFF_ENC1_SPEED  = 0x0098
OFF_ENC0_DELAY  = 0x0060
OFF_ENC1_DELAY  = 0x00a0
OFF_SCOPE_ADDR  = 0x000c
OFF_SCOPE_OFFSET= 0x0010
OFF_SCOPE_SIZE  = 0x0014
OFF_DEBUG       = 0x0018
OFF_CAP_DELAY   = 0x00c4


class Capture(_pru_adc.Capture):
    
	def __init__(self):
		self._mem = None
		_pru_adc.Capture.__init__(self)
		
		with open('/sys/class/uio/uio0/maps/map0/addr') as f:
			self._mem_addr = int(f.read().strip(), 16)
        
		with open('/sys/class/uio/uio0/maps/map0/size') as f:
			self._mem_size = int(f.read().strip(), 16)
		
		with open('/sys/class/uio/uio0/maps/map1/addr') as f:
			self._ddr_addr = int(f.read().strip(), 16)
        
		with open('/sys/class/uio/uio0/maps/map1/size') as f:
			self._ddr_size = int(f.read().strip(), 16)
        
		with open("/dev/mem", 'r+b') as f1:
			self._mem = mmap.mmap(f1.fileno(), self._mem_size, offset=self._mem_addr)
	
	def __del__(self):
		if self._mem:
			self._mem.close()
    
	def start(self):
		firmware = os.path.dirname(__file__) + '/firmware/firmware.bin'
		_pru_adc.Capture.start(self, firmware)
	
	def stop(self):
		self._set_word(OFF_FLAG, 1) # exit flag
    
	def close(self):
		_pru_adc.Capture.close(self)
		self._mem.close()
		self._mem = None
	
	@property
	def timer(self):
		"""
            Returns ADC timer value. This is the number of ADC capture cycles since driver start
            """
		return self._get_word(OFF_TIMER)
	
	@property
	def ema_pow(self):
		"""
            Returns EMA exponent. If zero, no EMA averaging
            """
		return self._get_word(OFF_EMA_POW)
	
	@ema_pow.setter
	def ema_pow(self, value):
		if 0 <= value <= 31:
			self._set_word(OFF_EMA_POW, value)
		else:
			raise ValueError("ema_pow must be in range 0-31")
	
	@property
	def values(self):
		return struct.unpack("LLLLLLLL", self._mem[OFF_VALUES:OFF_VALUES+8*4])
	
	@property
	def encoder0_pin(self):
		return struct.unpack("b", self._mem[OFF_ENC0_PIN:OFF_ENC0_PIN+1])[0]
	
	@encoder0_pin.setter
	def encoder0_pin(self, value):
		struct.pack_into('b', self._mem, OFF_ENC0_PIN, value)
	
	@property
	def encoder1_pin(self):
		return struct.unpack("b", self._mem[OFF_ENC1_PIN:OFF_ENC1_PIN+1])[0]
	
	@encoder1_pin.setter
	def encoder1_pin(self, value):
		struct.pack_into('b', self._mem, OFF_ENC1_PIN, value)
	
	@property
	def encoder0_threshold(self):
		return self._get_word(OFF_ENC0_THRESH)
	
	@encoder0_threshold.setter
	def encoder0_threshold(self, value):
		self._set_word(OFF_ENC0_THRESH, value)
    
	@property
	def encoder1_threshold(self):
		return self._get_word(OFF_ENC1_THRESH)
    
	@encoder1_threshold.setter
	def encoder1_threshold(self, value):
		self._set_word(OFF_ENC1_THRESH, value)
    
	@property
	def encoder0_values(self):
		return struct.unpack("LLLLL", self._mem[OFF_ENC0_VALUES:OFF_ENC0_VALUES+5*4])
	
	@property
	def encoder1_values(self):
		return struct.unpack("LLLLL", self._mem[OFF_ENC1_VALUES:OFF_ENC1_VALUES+5*4])
    
	@property
	def encoder0_delay(self):
		return self._get_word(OFF_ENC0_DELAY)
	
	@encoder0_delay.setter
	def encoder0_delay(self, value):
		self._set_word(OFF_ENC0_DELAY, value)
    
	@property
	def encoder1_delay(self):
		return self._get_word(OFF_ENC1_DELAY)
    
	@encoder1_delay.setter
	def encoder1_delay(self, value):
		self._set_word(OFF_ENC1_DELAY, value)
	
	@property
	def encoder0_ticks(self):
		return self._get_word(OFF_ENC0_TICKS)

	@property
	def encoder1_ticks(self):
		return self._get_word(OFF_ENC1_TICKS)
	
	@property
	def encoder0_speed(self):
		return self._get_word(OFF_ENC0_SPEED)
	
	@property
	def encoder1_speed(self):
		return self._get_word(OFF_ENC1_SPEED)

	@property
	def debug_value(self):
		return self._get_word(OFF_DEBUG)

	@property
	def cap_delay(self):
		return self._get_word(OFF_CAP_DELAY)

	@cap_delay.setter
	def cap_delay(self, value):
		self._set_word(OFF_CAP_DELAY, value)
    
	def _set_word(self, byte_offset, value):
		struct.pack_into('L', self._mem, byte_offset, value)
	
	def _get_word(self, byte_offset):
		return struct.unpack("L", self._mem[byte_offset:byte_offset+4])[0]
	
	def oscilloscope_init(self, offset, numsamples):
		if numsamples * 4 > self._ddr_size:
			raise ValueError("numsamples is too large. Limit is (determined by DDR memory size): " + str(self._ddr_size//4))
		self._set_word(OFF_SCOPE_ADDR, self._ddr_addr)
		self._set_word(OFF_SCOPE_OFFSET, offset)
		self._set_word(OFF_SCOPE_SIZE, numsamples * 4)
    
	def oscilloscope_is_complete(self):
		return self._get_word(OFF_SCOPE_SIZE) == 0
	
	def oscilloscope_data(self, numsamples):
		out = array.array('L')
		with open("/dev/mem", 'r+b') as f1:
			ddr_offset = 0
			ddr_addr = self._ddr_addr
			if ddr_addr >= 0x80000000: # workaround of mmap bug
				ddr_offset = 0x70000000
				ddr_addr -= ddr_offset
			ddr = mmap.mmap(f1.fileno(), self._ddr_size + ddr_offset, offset=ddr_addr)
			out.fromstring(ddr[ddr_offset:ddr_offset + 4*numsamples])
			ddr.close()
		return out
