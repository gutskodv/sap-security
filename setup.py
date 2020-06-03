import sapsecurity
from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='sapsecurity',
    version=sapsecurity.__version__,
    packages=['sapsecurity', 'sapsecurity.checks', 'sapsecurity.sapgui', 'sapsecurity.excelreport'],
    url='https://github.com/gutskodv/sap-security',
    license='GPL v2',
    author='Dmitry Gutsko',
    author_email='gutskodv@gmail.com',
    description='SAP security analysis with SAP GUI scripting',
    entry_points={'console_scripts': [ 'sapsecurity = sapsecurity.sapanalysis:main', ], },
    install_requires=required,
)
