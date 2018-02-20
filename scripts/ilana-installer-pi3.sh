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
sudo apt-get update -y

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


python3 -m venv env
env/bin/python -m pip install --upgrade pip setuptools wheel
source env/bin/activate

pip install -r /home/pi/GassistPi/Requirements/GassistPi-pip-requirements.txt

pip install google-assistant-library==0.1.0
pip install google-assistant-grpc==0.1.0
pip install google-assistant-sdk==0.4.2
pip install google-assistant-sdk[samples]==0.4.2
pip install google-auth==1.3.0	google-auth-httplib2==0.0.3 google-auth-oauthlib==0.2.0
google-oauthlib-tool --client-secrets /home/pi/$credname --scope https://www.googleapis.com/auth/assistant-sdk-prototype --save --headless
googlesamples-assistant-devicetool register-model --manufacturer "Pi Foundation" \
          --product-name $prodname --type LIGHT --model $modelid
echo "While I'm testing the installed google ass., you ake a note of the generated Device-Id"
googlesamples-assistant-hotword --project_id $projid --device_model_id $modelid
