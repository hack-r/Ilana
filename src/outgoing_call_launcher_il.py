import sys
from twilio.rest import Client
print("Calling" + sys.argv[1])
print("")
print("Voice logic URL:" + sys.argv[2])
target_number = sys.argv[1]
grok_url      = sys.argv[2]

account_sid = "ACcbf46bb1408ffdd76a7a3e2c45ac4d22"
auth_token = "71f84dc95e1c3ce435c66b8ac56c4426"
client = Client(account_sid, auth_token)

# Start a phone call
call = client.calls.create(
    to="+1"+target_number,
    from_="972526857154",
    url=grok_url
)

print(call.sid)

