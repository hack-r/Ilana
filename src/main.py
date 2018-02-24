#!/usr/bin/env python3

"""Run a recognizer using the Google Assistant Library.

The Google Assistant Library has direct access to the audio API, so this Python
code doesn't need to record audio. Hot word detection "OK, Google" is supported.

The Google Assistant Library can be installed with:
    env/bin/pip install google-assistant-library==0.0.2

It is available for Raspberry Pi 2/3 only; Pi Zero is not supported.
"""

import logging
import subprocess
import sys
import os

import aiy
import aiy.assistant.auth_helpers
import aiy.audio
import aiy.voicehat
from google.assistant.library import Assistant
from google.assistant.library.event import EventType
import aiy.cloudspeech

import twilio
#import outgoing_call_message_server

# CloudSpeech Recognizer
recognizer = aiy.cloudspeech.get_recognizer()

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)


def place_call():
    aiy.audio.say('Ilana is ready to place the call. Do you confirm?')
    if(2<1):
        outgoing_call_message()

def power_off_pi():
    aiy.audio.say('Good bye!')
    subprocess.call('sudo shutdown now', shell=True)


def reboot_pi():
    aiy.audio.say('See you in a bit!')
    subprocess.call('sudo reboot', shell=True)


def say_ip():
    ip_address = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True)
    aiy.audio.say('My IP address is %s' % ip_address.decode('utf-8'))


def process_event(assistant, event):
    button = aiy.voicehat.get_button()
    led = aiy.voicehat.get_led()
    
    status_ui = aiy.voicehat.get_status_ui()
    if event.type == EventType.ON_START_FINISHED:
        status_ui.status('ready')
        if sys.stdout.isatty():
            print('Address Ilana or Google directly. Alexa forthcoming. Press Ctrl+C to quit...')

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
        elif 'turn on the light' in text:
            led.set_state(aiy.voicehat.LED.ON)
        elif 'turn off the light' in text:
            print("testing123!")
            led.set_state(aiy.voicehat.LED.OFF)
        elif 'blink' in text:
            led.set_state(aiy.voicehat.LED.BLINK)
        elif 'repeat after me' in text:
            to_repeat = text.replace('repeat after me', '', 1)
            aiy.audio.say(to_repeat)

    elif event.type == EventType.ON_END_OF_UTTERANCE:
        status_ui.status('thinking')

    elif event.type == EventType.ON_CONVERSATION_TURN_FINISHED:
        status_ui.status('ready')

    elif event.type == EventType.ON_ASSISTANT_ERROR and event.args and event.args['is_fatal']:
        sys.exit(1)


def main():
    #recognizer.expect_phrase('Computer: Tea. Old grey. Hot.')

    credentials = aiy.assistant.auth_helpers.get_assistant_credentials()
    with Assistant(credentials) as assistant:
        for event in assistant.start():
            process_event(assistant, event)
    

    
    #aiy.audio.get_recorder().start()
    #usertext = recognizer.recognize()

if __name__ == '__main__':
    main()
