from setuptools import setup, find_packages

setup(name='naaya.content-semide',
      version='0.1',
      author='Eau de Web',
      author_email='alexandru.plugaru@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Naaya',
      ],
)