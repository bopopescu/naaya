from setuptools import setup, find_packages

setup(name='naaya.monitor',
      version='1.1',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='https://svn.eionet.europa.eu/repositories/Naaya/trunk/eggs/naaya.monitor',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      entry_points={'console_scripts': [
          'add_monitor_stats = naaya.monitor.monitor:add_monitor_stats',
      ]},
)
