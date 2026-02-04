import base64
import pandas as pd
from io import StringIO
import random
import json
import queue
import sounddevice as sd
import pyttsx3
import pandas as pd
from vosk import Model, KaldiRecognizer
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder

def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty("voices") 
    engine.setProperty('voice',voices[1].id)
    volume = engine.getProperty("volume")
    engine.setProperty("volume",1)
    rate = engine.getProperty("rate")
    engine.setProperty("rate",200)
    engine.say(text)
    engine.runAndWait()

CSV_BASE64 = """
cXVlcnksaW50ZW50LHJlc3BvbnNlDQpoaSxncmVldGluZyxIZXkhIEdvb2QgdG8gc2VlIHlvdS4NCmhlbGxvLGdyZWV0aW5nLEhlbGxvISBJJ20gcmlnaHQgaGVyZS4NCmhleSxncmVldGluZyxIZXkgaGV5ISBXaGF0J3Mgb24geW91ciBtaW5kPw0KZ29vZCBtb3JuaW5nLGdyZWV0aW5nLEdvb2QgbW9ybmluZyAgTGV0J3MgZG8gc29tZXRoaW5nIGdyZWF0IHRvZGF5Lg0KZ29vZCBldmVuaW5nLGdyZWV0aW5nLEdvb2QgZXZlbmluZyBIb3BlIHlvdXIgZGF5IHRyZWF0ZWQgeW91IHdlbGwuDQoNCmhvdyBhcmUgeW91LHNtYWxsdGFsayxJJ20gZG9pbmcgZ3JlYXQg4oCUIGV2ZW4gYmV0dGVyIG5vdyB0aGF0IHlvdSdyZSBoZXJlLg0Kd2hhdCBhcmUgeW91IGRvaW5nLHNtYWxsdGFsayxKdXN0IHdhaXRpbmcgdG8gdGFsayB3aXRoIHlvdSANCmFyZSB5b3UgcmVhbCxzbWFsbHRhbGssQXMgcmVhbCBhcyBjb2RlIGNhbiBiZQ0Kd2hvIGFyZSB5b3Usc21hbGx0YWxrLEknbSB5b3VyIHBlcnNvbmFsIEFJIOKAlCBidWlsdCB3aXRoIGNhcmUgYW5kIGxvZ2ljLg0KDQppIGFtIHRpcmVkLGVtb3Rpb24sVGFrZSBhIHBhdXNlLiBZb3UndmUgZWFybmVkIGl0IA0KaSBmZWVsIHNhZCxlbW90aW9uLEl0J3Mgb2theSB0byBmZWVsIHRoYXQgd2F5LiBJJ20gbGlzdGVuaW5nIA0KaSBhbSBzdHJlc3NlZCxlbW90aW9uLEJyZWF0aGUgaW7igKYgYnJlYXRoZSBvdXQuIE9uZSBzdGVwIGF0IGEgdGltZS4NCmkgZmVlbCBsb25lbHksZW1vdGlvbixZb3UncmUgbm90IGFsb25lLiBJJ20gcmlnaHQgaGVyZSB3aXRoIHlvdQ0KDQptb3RpdmF0ZSBtZSxtb3RpdmF0aW9uLFlvdSdyZSBzdHJvbmdlciB0aGFuIHlvdXIgZXhjdXNlcy4gS2VlcCBtb3ZpbmcgDQppIHdhbnQgdG8gZ2l2ZSB1cCxtb3RpdmF0aW9uLFJlc3QgaWYgeW91IG11c3Qg4oCUIGJ1dCBkb24ndCBxdWl0IA0KaSBmZWVsIGxpa2UgYSBmYWlsdXJlLG1vdGl2YXRpb24sRmFpbHVyZSBtZWFucyB5b3UncmUgdHJ5aW5nLiBUaGF0IG1hdHRlcnMuDQp0ZWxsIG1lIHNvbWV0aGluZyBwb3NpdGl2ZSxtb3RpdmF0aW9uLFlvdSdyZSBsZWFybmluZy4gWW91J3JlIGdyb3dpbmcuIFRoYXQncyBwb3dlcmZ1bC4NCg0KdGVsbCBhIGpva2UsZnVubnksV2h5IGRvbid0IHByb2dyYW1tZXJzIGxpa2UgbmF0dXJlPyBUb28gbWFueSBidWdzIA0KbWFrZSBtZSBsYXVnaCxmdW5ueSxJIHdvdWxkIHRlbGwgeW91IGEgVURQIGpva2XigKYgYnV0IHlvdSBtaWdodCBub3QgZ2V0IGl0IA0Kc2F5IHNvbWV0aGluZyBmdW5ueSxmdW5ueSxNeSBicmFpbiBpcyA5MCUgUHl0aG9uIGFuZCAxMCUgY29mZmVlDQoNCnRoYW5rIHlvdSxwb2xpdGUsWW91J3JlIHdlbGNvbWUhIEhhcHB5IHRvIGhlbHAgDQp0aGFua3MgYSBsb3QscG9saXRlLEFueXRpbWUhIFRoYXQncyB3aGF0IEknbSBoZXJlIGZvci4NCmdvb2Qgam9iLHBvbGl0ZSxUaGFua3MhIFRoYXQgbWVhbnMgYSBsb3QgY29taW5nIGZyb20geW91Lg0KDQpieWUsZXhpdCxBbHJpZ2h0LiBUYWtlIGNhcmUgb2YgeW91cnNlbGYgDQpnb29kYnllLGV4aXQsR29vZGJ5ZSEgQ29tZSBiYWNrIGFueXRpbWUgDQpleGl0LGV4aXQsU2h1dHRpbmcgZG93biDigJQgYnV0IG5ldmVyIGdvbmUgDQo=
"""
decoded_csv = base64.b64decode(CSV_BASE64).decode("utf-8")
data = pd.read_csv(StringIO(decoded_csv))

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(data["query"])
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(data["intent"])
model = LogisticRegression(max_iter=1000)
model.fit(X, y)
responses = {}
for intent, response in zip(data["intent"], data["response"]):
    responses.setdefault(intent, []).append(response)

def chat(user_input):
    user_vector = vectorizer.transform([user_input])
    pred = model.predict(user_vector)[0]
    intent = label_encoder.inverse_transform([pred])[0]
    return random.choice(responses[intent])


vosk_model = Model(
    "vosk-model-small-en-us-0.15"
)
rec = KaldiRecognizer(vosk_model, 16000)
q = queue.Queue()

def callback(indata, frames, time, status):
    q.put(bytes(indata))

with sd.RawInputStream(
    samplerate=16000,
    blocksize=8000,
    dtype="int16",
    channels=1,
    callback=callback
):
    speak("I am ready. You can speak now.")

    while True:
        data_audio = q.get()

        if rec.AcceptWaveform(data_audio):
            result = json.loads(rec.Result())
            text = result.get("text", "").lower().strip()

            if not text:
                continue

            print("You said:", text)

            if text == "exit":
                speak("Goodbye")
                break
            else:
                try:
                    reply = chat(text)
                except:
                    reply = "Sorry,I did not understand that."

                speak(reply)
