import sapsec
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='sapsec',
    version=sapsec.__version__,
    packages=find_packages(),
    url='https://github.com/gutskodv/sap-security',
    license='GPL v2',
    author='Dmitry Gutsko',
    author_email='gutskodv@gmail.com',
    description='SAP security analysis tool using SAP GUI scripting',
    long_description_content_type="text/markdown",
    long_description=long_description,
    entry_points={'console_scripts': ['sapsec = sapsec.sapanalysis:main', ], },
    install_requires=required,
    include_package_data=True
)
# packages=['sapsec', 'sapsec.checks', 'sapsec.sapgui', 'sapsec.excelreport'],
