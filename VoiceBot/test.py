import azure.cognitiveservices.speech as speechsdk
import openai
import os
from dotenv import load_dotenv
import streamlit as st


st.write("**Your input:**")
input = st.empty()
st.write("**ChatBot:**")
output = st.empty()



load_dotenv(r'C:\Users\bgraziadei\OneDrive - Maxaro\Documenten\GitHub\MaxaroProjects\VoiceBot\voiceBot.env')

openai.api_key = os.environ.get('api_key')
openai.api_base = os.environ.get('api_base')
openai.api_type = os.environ.get('api_type')
openai.api_version = os.environ.get('api_version')

speech_key, service_region = "f89395d5832043ffa61704e4498a0954", "WestEurope"

with open(r"C:\Users\bgraziadei\OneDrive - Maxaro\Documenten\GitHub\MaxaroProjects\VoiceBot\SystemMessage.txt") as f:
    sys_message = f.read()

conversation = [{"role": "system", "content": sys_message}]


def generate_response(prompt):
    conversation.append({"role": "user", "content":prompt})
    completion=openai.ChatCompletion.create(
        engine = "PvA",
        model="gpt-3.5-turbo",
        messages = conversation
    )
    
    message=completion.choices[0].message.content
    return message


def recognition():
    while True:
        result = ""
        text = ""
        input.write("*Speak now...*")
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        speech_config.speech_synthesis_voice_name = "en-US-GuyNeural"

        # Creates a speech synthesizer using the default speaker as audio output.
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)


        text = speech_recognizer.recognize_once().text

        if text:
            input.write(text)
            if text == "exit." or text == "Exit.":
                break
            result = generate_response(text)
            conversation.append({"role": "assistant", "content":result})

        if result:
            output.write(result)
            speech_synthesizer.speak_text_async(result).get()


if __name__ == "__main__":
    recognition()