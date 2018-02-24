from flask import Flask
from twilio.twiml.voice_response import VoiceResponse
import sys
print("The 2 required args are message and route. Hopefully you gave me that...")

message = sys.argv[1]
route = sys.argv[2]
app = Flask(__name__)


@app.route("/" + route, methods=['GET', 'POST'])
def answer_call():
    """Respond to incoming phone calls with a brief message."""
    # Start our TwiML response
    resp = VoiceResponse()

    # Read a message aloud to the caller
    resp.say(message, voice='alice')

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)

