# 727-controller

This repo contains the Showplayer and Showmaker programs which drive the 727 at MSI.

## Installation

These programs currently run on Python 3.8 through 3.12

 1. Install a compatible python version
 2. Clone this repo to the hard drive
 3. `python -m venv venv`
 4. 
    - Linux: `source ./venv/bin/activate`
    - Windows: TBD
 5. `python -m pip install -r requirements.txt`


 ## Running

 To run Showplayer (with venv active): `python showplayer_cuelist.py`

 To run Showmaker (with venv active): `python showmaker_cuelist.py`

 ## Installing

 1. Install Git (https://git-scm.com/downloads)
 2. Install Python (Tested up to version 3.11) (https://www.python.org/downloads/)
 3. From a command line, run `git clone https://github.com/jglassmsi/showplayer`
 4. From a command line, run `python -m venv venv`
 5. Activate the new virtual environment:
   - Windows: ./venv/scripts/activate.bat or ./venv/scripts/activate.ps1
   - Nix: source ./venv/bin/activate
 6. Run `python -m pip install -r requirements.txt`
 7. Install drivers for your USB/Serial dongle
 8. Run showplayer or showmaker as above.