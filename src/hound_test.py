#!/usr/bin/env python3

# NOTE: this example requires PyAudio because it uses the Microphone class

import speech_recognition as sr

# obtain audio from the microphone
r = sr.Recognizer()
with sr.Microphone() as source:
    print("Ilana is listening...")
    audio = r.listen(source)


# recognize speech using Houndify
HOUNDIFY_CLIENT_ID = "A4B6HG2n7DClAKukHZxKKw=="  # Houndify client IDs are Base64-encoded strings
HOUNDIFY_CLIENT_KEY = "GXzUAWYlLwrdTVpYBCQQiWFW8GTV-ju542yYsXcLLnZdvZjVu7QlVJRNZMYMfx_yJMdkwcq9szPzSZDdZ0MG-g=="  # Houndify client keys are Base64-encoded strings


text = r.recognize_houndify(audio, 
							client_id  = HOUNDIFY_CLIENT_ID, 
							client_key = HOUNDIFY_CLIENT_KEY
							#, show_all   = True
							)

print(type(text))
try:
	print("Ilana (via Houndify) thinks you said " + text)
except sr.UnknownValueError:
	print("Try to speak more clearly. You're not making any sense.")
except sr.RequestError as e:
	print("Could not request results from Houndify service; {0}".format(e))
if 'Computer' in text:
	print("SUCESS!! I heard you say my name.")

