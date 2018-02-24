from flask import Flask
from twilio.twiml.voice_response import VoiceResponse

app = Flask(__name__)


@app.route("/answer", methods=['GET', 'POST'])
def answer_call():
    """Respond to incoming phone calls with a brief message."""
    # Start our TwiML response
    resp = VoiceResponse()

    # Read a message aloud to the caller
    resp.say("Shalom. You've reached Eye lana. Thank you for calling! Yom tov.", voice='alice')

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
