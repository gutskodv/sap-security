# SAP security analysis tool using sap gui scripting

## Table of contents

* [ToC](#table-of-contents)
* [Python installation](#python-installation)
* [Install](#install)
* [Before running](#before-running)
* [Usage](#usage)
* [Predefined SAP security packs](#predefined-sap-security-packs)

## Python installation
1. Download [last version of Python 3.x installer](https://www.python.org/downloads/)
2. Run the installer
3. While installation choose folowing option:
    - Add python 3.x to PATH

## Install

### Pip installation (recomended)
Installation is easy. Run in windows console (command line interpreter - cmd):
```sh
pip install sapsec
```
If your computer is behind a proxy set additional option --proxy in following format: 
```sh
pip install sapsec --proxy http://user:password@proxyserver:port
```

### Installation from github
If for some reason the installation was not successful (with pip) there is an opportunity to install sapsec from github source files.
1. Download [zip archive](https://github.com/gutskodv/sap-security/archive/master.zip) with project source codes. Or use git clone:
```sh
git clone https://github.com/gutskodv/sap-security.git
```
2. Unpack files from dowloaded zip archive. And go to project directory with setup.py file.
3. Ugrade pip, Install Wheel package, Collect sapsec package:
```sh
python -m pip install --upgrade pip
pip install wheel
python setup.py bdist_wheel
```
4. Install sapsec package from generaed python wheel in dist subdirectory:
```sh
python setup.py dist\sapsec*.whl
```

### Requirements
You can manually intall requirements if they were not installed in automatic mode.
1. PyWin32 (Python extensions for Microsoft Windows Provides access to much of the Win32 API, the ability to create and use COM objects, and the Pythonwin environment).
```sh
pip install pywin32
```
2. XlsxWriter (Python module for writing files in the Excel 2007+ XLSX file format).
```sh
pip install xlsxwriter
```
3. PyYaml (a YAML parser and emitter for Python).
```sh
pip install xlsxwriter
```

## Before running
1. Сheck that gui scripting is enabled on the SAP server. The parameter sapgui/user_scripting should be set to TRUE. If the parameter value is currently set to FALSE, change it before start. For more information about GUI scripting read [the article](https://blogs.sap.com/2012/10/08/introduction-to-sap-gui-scripting/).
2. If the paramaeter sapgui/user_scripting_per_user is also set to TRUE, make sure the SAP user is assigned S_SCR:ACTVT=16 (Authorization for SAP GUI Scripting).

## Usage
1. Run SAP Logon application.
2. Log in to the SAP server (enter your user name and password).
3. Go to windows console (command line interpreter - cmd). Change directory
4. Run sapsec:
```sh
sapsec
```
or
```sh
python -m sapsec
```
or you'd like use your own config:
```sh
sapsec --rules rules_config.yaml
```

5. Inspect generated excel report (in directory you choosen).

## Predefined SAP security packs
1. Weak(redundant) password hashes (BCODE, PASSCODE) in SAP tables.
