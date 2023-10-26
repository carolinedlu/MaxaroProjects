
import azure.cognitiveservices.speech as speechsdk


speech_key, service_region = "f89395d5832043ffa61704e4498a0954", "WestEurope"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

speech_config.speech_synthesis_voice_name = "en-US-GuyNeural"
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

print("Type some text that you want to speak...")
text = input()

speech_synthesizer.speak_text_async(text).get()