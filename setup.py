from setuptools import setup

setup(
    name='sapsecurity',
    version='0.1',
    packages=['sapsecurity', 'sapsecurity.checks', 'sapsecurity.sapgui', 'sapsecurity.excelreport'],
    url='https://github.com/gutskodv/sap-security',
    license='GPL v2',
    author='Dmitry Gutsko',
    author_email='gutskodv@gmail.com',
    description='SAP security analysis with SAP GUI scripting'
)
