from setuptools import setup, find_packages

setup(name='naaya.semide',
      version='0.1',
      author='Eau de Web',
      author_email='office@eaudeweb.ro',
      url='http://naaya.eaudeweb.ro',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Naaya',
          'python-memcached'
          #'edw-ZOpenArchives',
          #'edw-reportlab',
          #'naaya.calendar',
          #'naaya.forum',
          #'naaya.glossary',
          #'naaya.helpdeskagent',
          #'naaya.linkchecker',
          #'naaya.thesaurus',
          #'RDFCalendar',
          #'RDFSummary',
          #'RDFSummary',
      ],
)
