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

Setting up on a new computer:

Install Git
Install Python (3.12)
git clone https://github.com/jglassmsi/showplayer

python -m venv venv

(activate venv):
 - Windows: ./venv/scripts/activate.bat or ./venv/scripts/activate.ps1
 - Nix: source ./venv/bin/activate

python -m pip install -r requirements.txt

Run:
python showplayer.py
