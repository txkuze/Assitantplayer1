import os
from pydub import AudioSegment
from pydub.generators import Sine
from config import config

def generate_silence_file():
    try:
        os.makedirs(config.VOICE_CACHE_DIR, exist_ok=True)

        silence = AudioSegment.silent(duration=60000)

        output_path = os.path.join(config.VOICE_CACHE_DIR, "silence.mp3")
        silence.export(output_path, format="mp3")

        print(f"Silence file created at: {output_path}")
        return output_path

    except Exception as e:
        print(f"Error generating silence file: {e}")
        return None

if __name__ == "__main__":
    generate_silence_file()
