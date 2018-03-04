# Copyright (C) 2017 Google Inc.
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

from __future__ import print_function

from enum import Enum
from json import loads

try:
    import queue as queue
except ImportError:
    import Queue as queue


class EventType(Enum):
    """The Assistant library has finished starting."""
    ON_START_FINISHED = 0
    """Indicates a new turn has started.

    The Assistant is currently listening, waiting for a user query. This could
    be the result of hearing the hotword or start_conversation() being called
    on the Assistant.
    """
    ON_CONVERSATION_TURN_STARTED = 1
    """The Assistant timed out waiting for a discernable query.

    This could be caused by a mistrigger of the Hotword or the Assistant could
    not understand what the user said.
    """
    ON_CONVERSATION_TURN_TIMEOUT = 2
    """The Assistant has stopped listening to a user query.

    The Assistant may not have finished figuring out what the user has said but
    it has stopped listening for more audio data.
    """
    ON_END_OF_UTTERANCE = 3
    """The Assistant has determined the final recognized speech.

    Args:
        text(str): The final text interpretation of a user's query.
    """
    ON_RECOGNIZING_SPEECH_FINISHED = 5
    """The Assistant is starting to respond by voice.

    The Assistant will be responding until ON_RESPONDING_FINISHED is received.

    Args:
        is_error_response(bool): True means a local error TTS is being played,
            otherwise the Assistant responds with a server response.
    """
    ON_RESPONDING_STARTED = 6
    """The Assistant has finished responding by voice."""
    ON_RESPONDING_FINISHED = 7
    """The Assistant successfully completed its turn but has nothing to say."""
    ON_NO_RESPONSE = 8
    """The Assistant finished the current turn.

    This includes both processing a user's query and speaking the
    full response.

    Args:
        with_follow_on_turn(bool): If True, the Assistant is expecting a
            follow up interaction from the user. The microphone will be
            re-opened to allow the user to answer a follow-up question.
    """
    ON_CONVERSATION_TURN_FINISHED = 9
    """Indicates that an alert has started sounding.

    This alert will continue until ON_ALERT_FINISHED with the same
    |alert_type| is received. Only one alert should be active at any given
    time.

    Args:
        alert_type(int): The id of the Enum representing the currently
            sounding type of alert.
    """
    ON_ALERT_STARTED = 10
    """Indicates the alert of |alert_type| has finished sounding.

    Args:
        alert_type(int): The id of the Enum representing the type of alert
            which just finished.
    """
    ON_ALERT_FINISHED = 11
    """Indicates if the Assistant library has encountered an error.

    Args:
        is_fatal(bool): If True then the Assistant will be unable to recover
            and should be restarted.
    """
    ON_ASSISTANT_ERROR = 12
    """Indicates that the Assistant is currently listening or not.

    start() will always generate an ON_MUTED_CHANGED to report the initial
    value.

    Args:
        is_muted(bool): If True then the Assistant is not currently listening
            for its hotword and will not respond to user queries.
    """
    ON_MUTED_CHANGED = 13


class AlertType(Enum):
    ALARM = 0
    TIMER = 1


class Event(object):
    """An event generated by the Assistant.

    Attributes:
        type(EventType): The type of event that was generated.
        args(dict): Argument key/value pairs associated with this event.
    """

    def __init__(self, type_value, json_args):
        """Initializes a new Assistant event.

        The native Assistant will generate events such as:

            type_value: 5
            json_args: "{ 'text': 'what time is it' }"

        which are then converted to a more Pythonic representation here.

        Args:
            type_value(int): The numeric value of the EventType.
            json_args(str): A JSON string object representing the args.
        """
        self._type = EventType(type_value)
        self._args = (loads(json_args.decode(encoding='UTF-8'))
                      if json_args else None)

    @property
    def type(self):
        return self._type

    @property
    def args(self):
        return self._args

    def __str__(self):
        out = self.type.name
        if (self.args):
            out += ':\n  ' + str(self.args)
        return out


class IterableEventQueue(queue.Queue):
    """Extends queue.Queue to add an __iter__ interface."""

    def __init__(self, timeout=3600):
        """Initializes an iterable queue.Queue.

        Args:
            timeout(int): The number of seconds to sleep, waiting for an event
                when iterating. Lower numbers mean the event loop will be
                active more often (and consuming CPU cycles).
        """
        super(IterableEventQueue, self).__init__(maxsize=32)
        self._timeout = timeout

    def offer(self, event):
        """Offer an event to put in the queue.

        If the queue is currently full the event will be logged but not added.

        Args:
            event(Event): The event to try to add to the queue.
        """
        try:
            self.put(event, block=False)
        except queue.Full:
            # TODO(jordanjtw): We should log or throw an exception with the
            # ignored event.
            pass

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        while True:
            try:
                return self.get(block=True, timeout=self._timeout)
            except KeyboardInterrupt:
                raise StopIteration()
            except queue.Empty:
                pass
