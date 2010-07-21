from setuptools import setup, find_packages

setup(name='naaya.semide',
    version='1.1',
    author='Eau de Web',
    author_email='office@eaudeweb.ro',
    url='http://naaya.eaudeweb.ro',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Naaya',
        'Products.NaayaCalendar',
        'Products.NaayaForum',
        'Products.NaayaGlossary',
        'Products.NaayaHelpDeskAgent',
        'Products.NaayaLinkChecker',
        'Products.NaayaThesaurus',
        'Products.RDFCalendar',
        'Products.RDFSummary',
        'edw-ZOpenArchives',
        'edw-reportlab',
        'python-memcached',
    ]
)
