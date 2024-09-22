import os, re
import botocore.response
import flet as ft
from boto3 import Session
from typing import Callable
from functools import wraps
import speech_recognition as sr

def supress_exception(*args: type[Exception]) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*argsinner, **kwargs):
            try:
                return func(*argsinner, **kwargs)
            except args as e:
                print(f"Supressed Error in {func.__qualname__}: {e}")
        return wrapper
    return decorator

ses = Session(region_name="us-east-1")
polly = ses.client("polly")

@supress_exception(Exception)
def speak_ssml(ssml: str) -> None:
    response = polly.synthesize_speech(
        Engine="generative",
        OutputFormat="mp3",
        TextType="ssml",
        Text=ssml,
        VoiceId="Ruth"
    )
    print(response)
    stream: botocore.response.StreamingBody = response["AudioStream"]
    with open("speech.mp3", "wb") as f:
        f.write(stream.read())
    os.system("play speech.mp3")

def record_and_recognise(page: ft.Page,btn: ft.IconButton, input: ft.TextField, sendbtn: ft.IconButton| None= None) -> None:
    btn.disabled = True
    if sendbtn: sendbtn.disabled = True
    page.update()
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
    print("Recognizing...")
    try:
        text = r.recognize_google(audio) #type: ignore
        print(f"Google Speech Recognition thinks you said: {text}")
        input.value = text
    except sr.UnknownValueError:
        input.value = "Google Speech Recognition could not understand the audio"
    except sr.RequestError as e:
        input.value = f"Could not request results from Google Speech Recognition service; {e}"
    btn.disabled = False
    if sendbtn:
        sendbtn.disabled = False
        sendbtn.on_click(None)
    page.update()
def clean_text(text: str) -> tuple[str, str]:
    break_regex = r"#\[break\=([0-9]+(\.[0-9]+)?)s\]"
    url_regex = r"\[([^\]]+)\]\(([^\)]+)\)"
    command_regex = r"<<<([a-zA-Z0-9_]+:({[^}]+}){0,1})>>>"
    ipa_regex = r"#\[IPA\=([^\]]+)\]\s*\(([^\)]+)\)"
    language_regex = r"#\[lang\=([a-zA-Z0-9_]+)\]\s*\(([^\)]+)\)"
    render, speech = re.sub(break_regex, "", text), re.sub(break_regex, r'<break time="\1s"/>', text)
    render, speech = re.sub(ipa_regex, r"\2 \(pronounced as \1\)", render), re.sub(ipa_regex, r'<phoneme alphabet="ipa" ph="\1">\2</phoneme>', speech) # Remove IPA in render, replace with normal text in speech
    render, speech = re.sub(language_regex, r"\2", render), re.sub(language_regex, r'<lang xml:lang="\1">\2</lang>', speech) # Remove language in render, replace with normal text in speech
    speech = re.sub(url_regex, r"\1", speech) # Remove URLs in speech
    speech = re.sub(command_regex, "", speech) # Remove command calls in speech
    return render, speech
# if __name__ == "__main__":
#     speak_ssml("""
# <speak>
# In *Resident Evil Village*, the main villains are. <break time="0.5s"/>
# One, Lady Dimitrescu, a towering vampire lady who rules over her castle and has a thirst for blood. <break time="0.5s"/>
# Two, Donna Beneviento, a doll maker who controls a creepy doll named Angie, and her area is filled with psychological horror. <break time="0.5s"/>
# Three, Salvatore Moreau, a grotesque creature who is part fish and part human, living in a swampy area. <break time="0.5s"/>
# Four, Heisenberg, a mechanic with the ability to control metal and machinery, who has his own agenda against the main antagonist. <break time="0.5s"/>
# And five, Mother Miranda, the main antagonist, she is a powerful cult leader with a dark past and sinister motives. <break time="0.5s"/>
# These villains add a unique flavor to the survival horror experience, each with their own horrifying abilities and backstories.
# </speak>""")
