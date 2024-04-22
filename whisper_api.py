import openai
import os

openai.api_key = "YOUR_OPENAI_API_KEY"

def whisper_speech_to_text(audio_file):
    with open(audio_file, "rb") as f:
        response = openai.File.create(
            file=f,
            purpose="transcription"
        )
    return response['transcription']
