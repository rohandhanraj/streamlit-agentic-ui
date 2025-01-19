# Import the required module for text <<===>> speech conversion
from gtts import gTTS
import speech_recognition as sr

# Import audio play library
import base64
import streamlit as st
import os


def transcribe(wav_audio_path):
    file_audio = sr.AudioFile(wav_audio_path)
    # use the audio file as the audio source                                        
    r = sr.Recognizer()
    with file_audio as source:
        audio_text = r.record(source)
    try:
        transcript = r.recognize_google(audio_text)
    except Exception as e:
        transcript_error = f"Exception Encountered [Transcription] :: {e.__str__()}"
        transcript = None
        print(transcript_error)
    return transcript

def gen_speech(text, audio_out_path):
    # Create a text to speech engine
    language = 'en'

    # Passing the text and language to the engine, 
    # here we have marked slow=False. Which tells 
    # the module that the converted audio should 
    # have a high speed
    myobj = gTTS(text=text, lang=language, slow=False)

    # Saving the converted audio in a mp3 file named
    # welcome 
    myobj.save(audio_out_path)

def speak(mp3_audio_path):
    # Play the mp3 file
    with open(mp3_audio_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")
    md = f"""
    <audio controls autoplay>
    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
    </audio>
    """
    st.markdown(md, unsafe_allow_html=True)