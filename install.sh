#!/bin/sh

# Separate script to download the Delta Wi-Fi Positioning app,
# install all requirements with pip3,
# and launch the app with python3.


git clone https://github.com/tonysln/delta-wifi-pos.git

echo "Opening repository folder..."
cd delta-wifi-pos

echo "Installing pip requirements..."
pip3 install -r requirements.txt

echo "Launching app..."
python3 app.py

echo "Done."