import _pru_adc
import glob
import re
import os
import mmap
import struct
import time

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
		self._set_word(0x0008, 1) # exit flag
    
	def close(self):
		_pru_adc.Capture.close(self)
		self._mem.close()
		self._mem = None
	
	@property
	def timer(self):
		"""
            Returns ADC timer value. This is the number of ADC capture cycles since driver start
            """
		return self._get_word(0x0004)
	
	@property
	def ema_pow(self):
		"""
            Returns EMA exponent. If zero, no EMA averaging
            """
		return self._get_word(0x001c)
	
	@ema_pow.setter
	def ema_pow(self, value):
		if 0 <= value <= 31:
			self._set_word(0x001c, value)
		else:
			raise ValueError("ema_pow must be in range 0-31")
	
	@property
	def values(self):
		return struct.unpack("LLLLLLLL", self._mem[0x0020:0x0020+8*4])
	
	@property
	def encoder0_pin(self):
		return struct.unpack("b", self._mem[0x0040:0x0040+1])[0]
	
	@encoder0_pin.setter
	def encoder0_pin(self, value):
		struct.pack_into('b', self._mem, 0x0040, value)
	
	@property
	def encoder1_pin(self):
		return struct.unpack("b", self._mem[0x0041:0x0041+1])[0]
	
	@encoder1_pin.setter
	def encoder1_pin(self, value):
		struct.pack_into('b', self._mem, 0x0041, value)
	
	@property
	def encoder0_threshold(self):
		return self._get_word(0x44)
	
	@encoder0_threshold.setter
	def encoder0_threshold(self, value):
		self._set_word(0x44, value)
    
	@property
	def encoder1_threshold(self):
		return self._get_word(0x64)
    
	@encoder1_threshold.setter
	def encoder1_threshold(self, value):
		self._set_word(0x64, value)
    
	@property
	def encoder0_values(self):
		return struct.unpack("LLLLL", self._mem[0x0048:0x0048+5*4])
	
	@property
	def encoder1_values(self):
		return struct.unpack("LLLLL", self._mem[0x0068:0x0068+5*4])
    
	def _set_word(self, byte_offset, value):
		struct.pack_into('L', self._mem, byte_offset, value)
	
	def _get_word(self, byte_offset):
		return struct.unpack("L", self._mem[byte_offset:byte_offset+4])[0]
	
	def oscilloscope_capture_init(self, offset, numsamples):
		if numsamples * 4 > self._ddr_size:
			raise ValueError("numsamples is too large. Limit is (determined by DDR memory size): " + str(self._ddr_size//4))
		self._set_word(0x0c, self._ddr_addr)
		self._set_word(0x10, offset)
		self._set_word(0x14, numsamples * 4)
    
	def oscilloscope_capture_complete(self):
		return self._get_word(0x14) == 0
	
	def oscilloscope_capture_data(self, numsamples):
		out = []
		with open("/dev/mem", 'r+b') as f1:
			ddr_offset = 0
			ddr_addr = self._ddr_addr
			if ddr_addr >= 0x80000000: # workaround of mmap bug
				ddr_offset = 0x70000000
				ddr_addr -= ddr_offset
			ddr = mmap.mmap(f1.fileno(), self._ddr_size + ddr_offset, offset=ddr_addr)
			for i in range(numsamples):
				out.append(struct.unpack("L", ddr[ddr_offset+i*4:ddr_offset+i*4+4])[0])
			ddr.close()
		return out

def workaround_mmap_bug(addr):
	print hex(addr)
	if addr > 0x7fffffff:
		print -1 - addr
		return 0x7fffffffff - addr
	return addr
