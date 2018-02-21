#!/bin/bash
set -o errexit

scripts_dir="$(dirname "${BASH_SOURCE[0]}")"

# make sure we're running as the owner of the checkout directory
RUN_AS="$(ls -ld "$scripts_dir" | awk 'NR==1 {print $3}')"
if [ "$USER" != "$RUN_AS" ]
then
    echo "This script must run as $RUN_AS, trying to change user..."
    exec sudo -u $RUN_AS $0
fi
clear
echo ""
read -r -p "Enter the your full credential file name including .json extension: " credname
echo ""
read -r -p "Enter the your Google Cloud Console Project-Id: " projid
echo ""
read -r -p "Enter a product name for your device (product name should not have space in between): " prodname
echo ""

modelid=$projid-$(date +%Y%m%d%H%M%S )
echo "Your Model-Id used for the project is: $modelid" >> /home/pi/modelid.txt
cd /home/pi/

echo ""
echo ""
echo "Ilana is updating apt..."
echo ""
echo ""
sudo apt-get update -y

echo ""
echo ""
echo "Ilana is compiling and installing dependencies..."
echo ""
echo ""
sudo apt-get install libatlas-base-dev
sed 's/#.*//' /home/pi/Desktop/Ilana/Requirements/Ilana-system-requirements.txt | xargs sudo apt-get install -y
if [ ! -d /home/pi/.config/mpv/scripts/ ]; then
  mkdir -p /home/pi/.config/mpv/scripts/
fi
if [ -f /home/pi/Desktop/Ilana/src/end.lua ]; then
  mv /home/pi/Desktop/Ilana/src/end.lua /home/pi/.config/mpv/scripts/end.lua
fi
if [ -f /home/pi/Desktop/Ilana/src/mpv.conf ]; then
  mv /home/pi/Desktop/Ilana/src/mpv.conf /home/pi/.config/mpv/mpv.conf
fi

echo ""
echo ""
echo "********************************************************"
echo "Ilana is setting up a Python 3.x virtual environment..."
echo "********************************************************"
python3 -m venv env
env/bin/python -m pip install --upgrade pip setuptools wheel
source env/bin/activate

echo ""
echo ""

echo "********************************************************"
echo "Ilana is installing requirements.txt into the virtual env..."
echo "********************************************************"

pip install -r /home/pi/Desktop/Ilana/Requirements/Ilana-pip-requirements.txt
sudo apt-get install libatlas-base-dev

echo "********************************************************"
echo "Ilana is installing Google libraries for Python..."
echo "********************************************************"

pip install google-assistant-library
pip install google-assistant-grpc
pip install google-assistant-sdk
pip install google-assistant-sdk[samples]
echo ""
echo ""

echo "********************************************************"
echo "Ilana is installing and implementing authentication..."
echo "********************************************************"

pip install google-auth	google-auth-httplib2 google-auth-oauthlib
google-oauthlib-tool --client-secrets /home/pi/$credname --scope https://www.googleapis.com/auth/assistant-sdk-prototype --save --headless
googlesamples-assistant-devicetool register-model --manufacturer "Pi Foundation" \
          --product-name $prodname --type LIGHT --model $modelid googlesamples-assistant-hotword --project_id $projid --device_model_id $modelid

echo ""
echo ""
echo "Ilana setup complete!"
