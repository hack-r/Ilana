#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Run a recognizer using the Google Assistant Library.

The Google Assistant Library has direct access to the audio API, so this Python
code doesn't need to record audio. Hot word detection "OK, Google" is supported.

The Google Assistant Library can be installed with:
    env/bin/pip install google-assistant-library==0.0.2

It is available for Raspberry Pi 2/3 only; Pi Zero is not supported.
"""

#from gmusicapi import Mobileclient
from google.assistant.library import Assistant
from google.assistant.library.event import EventType
#from googleapiclient.discovery import build
#from googleapiclient.errors import HttpError
#from googletrans import Translator
from gtts import gTTS
import RPi.GPIO as GPIO
#import aftership
import aiy
import aiy.assistant.auth_helpers
import aiy.audio
import aiy.cloudspeech
import aiy.voicehat
import feedparser
import json
import logging
import os
import os.path
import pafy
#import pychromecast
import re
import requests
import subprocess
import sys
import threading
import time
import twilio
import urllib.request
import snowboydecoder
import signal

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)

interrupted = False


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted
    
def launch_ilana():    
    print("It worked")
    recognizer = aiy.cloudspeech.get_recognizer()
    aiy.audio.get_recorder().start()
	
    while True:
        text = recognizer.recognize()
        if 'tell google' in text:
            tell_google()
        if 'my ip' in text:
            say_ip()
        if 'reboot the system' or 'reboot system' in text:
        	reboot_pi()
        if 'who cut off who' in text:
        	say_cut_off()
        if 'who is right' in text:
            say_jason_right()
        #if '' in text:
        #if '' in text:
        #if '' in text:
                
        else:    
            aiy.audio.say('You said ', text)
    
  
def power_off_pi():
    aiy.audio.say('Good bye!')
    #subprocess.call('sudo shutdown now', shell=True)

def process_event(assistant, event):
    status_ui = aiy.voicehat.get_status_ui()
    if event.type == EventType.ON_START_FINISHED:
        status_ui.status('ready')
        if sys.stdout.isatty():
            print('Say "OK, Google" then speak, or press Ctrl+C to quit...')

    elif event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        status_ui.status('listening')

    elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED and event.args:
        print('You said:', event.args['text'])
        text = event.args['text'].lower()
        if text == 'power off':
            assistant.stop_conversation()
            power_off_pi()
        elif text == 'reboot':
            assistant.stop_conversation()
            reboot_pi()
        elif text == 'ip address':
            assistant.stop_conversation()
            say_ip()

    elif event.type == EventType.ON_END_OF_UTTERANCE:
        status_ui.status('thinking')

    elif event.type == EventType.ON_CONVERSATION_TURN_FINISHED:
        status_ui.status('ready')

    elif event.type == EventType.ON_ASSISTANT_ERROR and event.args and event.args['is_fatal']:
        sys.exit(1)

def reboot_pi():
    aiy.audio.say('See you in a bit!')
    #subprocess.call('sudo reboot', shell=True)

def say_cut_off():
    aiy.audio.say('She cut you off')
    
def say_ip():
    ip_address = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True)
    aiy.audio.say('My IP address is %s' % ip_address.decode('utf-8'))
def say_jason_right():
    aiy.audio.say('Objectively speaking, Jason is right. I would trust his wisdom.')
    
def tell_google():
    with Assistant(credentials) as assistant:
        for event in assistant.start():
            process_event(assistant, event)	  

# Capture model from argument
if len(sys.argv) == 1:
    print("Error: need to specify model name")
    print("Usage: python ilana_snow.py ilana.pmdl")
    sys.exit(-1)

model = sys.argv[1]

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
print('Listening... Press Ctrl+C to exit')

# main loop
def main():
    credentials = aiy.assistant.auth_helpers.get_assistant_credentials()
    
    detector.start(detected_callback=launch_ilana,
        interrupt_check=interrupt_callback,
        sleep_time=0.03)

    detector.terminate()



if __name__ == '__main__':
    main()
