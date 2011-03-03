from setuptools import setup, find_packages

setup(name='edw-localizer',
      version='1.2.3.4', #EDW version .4 based on localizer 1.2.3
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
)
