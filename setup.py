import distribute_setup
distribute_setup.use_setuptools()

from setuptools import setup, Extension, find_packages

classifiers = ['Development Status :: 3 - Alpha',
               'Operating System :: POSIX :: Linux',
               'License :: OSI Approved :: MIT License',
               'Intended Audience :: Developers',
               'Programming Language :: Python :: 2.6',
               'Programming Language :: Python :: 2.7',
               'Programming Language :: Python :: 3',
               'Topic :: Software Development',
               'Topic :: Home Automation',
               'Topic :: System :: Hardware']

setup(name             = 'beaglebone_pru_adc',
      version          = '0.0.3',
      author           = 'Mike Kroutikov',
      author_email     = 'pgmmpk@gmail.com',
      description      = 'Fast analog sensor capture for Beaglebone Black',
      long_description = open('README.md').read(),
      license          = 'MIT',
      keywords         = 'BeagleBone PRU ADC',
      url              = 'https://github.com/pgmmpk/beaglebone_pru_adc/',
      classifiers      = classifiers,
      packages         = find_packages(),
      py_modules       = ['beaglebone_pru_adc'],
      package_data     = {'beaglebone_pru_adc': ['firmware/*.bin']},
      ext_modules      = [
          Extension('beaglebone_pru_adc._pru_adc', 
              ['src/pru_adc.c', 'prussdrv/prussdrv.c'],
              include_dirs = ['prussdrv', 'src']
          )
      ] 
)
