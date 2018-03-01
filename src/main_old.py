#!/usr/bin/env python3

"""Run a recognizer using the Google Assistant Library.

The Google Assistant Library has direct access to the audio API, so this Python
code doesn't need to record audio. Hot word detection "OK, Google" is supported.

The Google Assistant Library can be installed with:
    env/bin/pip install google-assistant-library==0.0.2

It is available for Raspberry Pi 2/3 only; Pi Zero is not supported
"""

from google.assistant.library import Assistant
from google.assistant.library.event import EventType
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googletrans import Translator
from gtts import gTTS
import RPi.GPIO as GPIO
import aftership
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
import pychromecast
import re
import requests
import subprocess
import subprocess
import sys
import threading
import time
import twilio
import urllib.request

logger = logging.getLogger('speech')



logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)


#def place_call():
#    aiy.audio.say('Ilana is ready to place the call. Do you confirm?')
#    if(2<1):
#        outgoing_call_message()

def power_off_pi():
    aiy.audio.say('Good bye!')
    subprocess.call('sudo shutdown now', shell=True)


def reboot_pi():
    aiy.audio.say('See you in a bit!')
    subprocess.call('sudo reboot', shell=True)


def say_ip():
    ip_address = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True)
    aiy.audio.say('My IP address is %s' % ip_address.decode('utf-8'))

class MyAssistant(object):
    """An assistant that runs in the background.
    The Google Assistant Library event loop blocks the running thread entirely.
    To encase it in Ilana, we need to run the event loop in a separate
    thread. Otherwise, the _ilana() method will never get a chance to
    be invoked.
    """

    def __init__(self):
        self._task = threading.Thread(target=self._run_task)
        self._can_start_conversation = False
        self._assistant = None

    def start(self):
        """Starts the assistant.
        Starts the assistant event loop and begin processing events.
        """
        self._task.start()

    def _run_task(self):
        credentials = aiy.assistant.auth_helpers.get_assistant_credentials()
        with Assistant(credentials) as assistant:
            self._assistant = assistant
            for event in assistant.start():
                self._process_event(event)

    def _process_event(self, event):
        status_ui = aiy.voicehat.get_status_ui()
        if event.type == EventType.ON_START_FINISHED:
            status_ui.status('ready')
            self._can_start_conversation = True

            # Wait for a conversation to begin
            ## aiy.voicehat.get_button().on_press(self._ilana)
            # CloudSpeech Recognizer
            recognizer = aiy.cloudspeech.get_recognizer()
            #recognizer.expect_phrase('Ilana')
	    recognizer.expect_hotword(['Google','Raspberry Pi'])
            while True:
                print('Listening...')
                text = recognizer.recognize()
                print(text)
                if text is None:
                    print('Sorry, I did not hear you.')
                else:
                    print('You said "', text, '"')
                    if 'Ilana turn on the LED' in text:
                        led.set_state(aiy.voicehat.LED.ON)
                    elif 'Ilana turn off the LED' in text:
                        led.set_state(aiy.voicehat.LED.OFF)
                    elif 'Eye lana blink' in text:
                        led.set_state(aiy.voicehat.LED.BLINK)
                    elif 'Ilana repeat after me' in text:
                        to_repeat = text.replace('repeat after me', '', 1)
                        aiy.audio.say(to_repeat)
                    elif 'Ilana self destruct' in text:
                        os._exit(0)
                    elif 'Ialana tell Google' in text:
                        self._ilana()

            if sys.stdout.isatty():
                print('Say "Speak to Ilana at your leisure...'
                      'Press Ctrl+C to quit...')

        elif event.type == EventType.ON_CONVERSATION_TURN_STARTED:
            self._can_start_conversation = False
            status_ui.status('listening')

        elif event.type == EventType.ON_END_OF_UTTERANCE:
            status_ui.status('thinking')

        elif event.type == EventType.ON_CONVERSATION_TURN_FINISHED:
            status_ui.status('ready')
            self._can_start_conversation = True

        elif event.type == EventType.ON_ASSISTANT_ERROR and event.args and event.args['is_fatal']:
            sys.exit(1)

    def _ilana(self):
        # Check if we can start a conversation. 'self._can_start_conversation'
        # is False when either:
        # 1. The assistant library is not yet ready; OR
        # 2. The assistant library is already in a conversation.
        if self._can_start_conversation:
            self._assistant.start_conversation()


def main():
    MyAssistant().start()


if __name__ == '__main__':
    main()
