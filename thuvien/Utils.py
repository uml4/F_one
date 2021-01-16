import pygame
from gtts import gTTS
import os
import wave

TOP_DIR = os.path.dirname(os.path.abspath(__file__))
DETECT_DING = os.path.join(TOP_DIR, "ding.wav")
DETECT_DONG = os.path.join(TOP_DIR, "dong.wav")

def text_to_speak(text):
    print("Bot: {}".format(text))
    tts = gTTS(text=text, lang='vi', slow=False)
    tts.save("sound2.mp3")
    # playsound.playsound("sound.mp3")
    pygame.mixer.init()

    pygame.mixer.music.set_volume(1.0)


    pygame.mixer.music.load("sound2.mp3")
    pygame.mixer.music.play()
    # os.remove("sound.mp3")

    while pygame.mixer.music.get_busy() == True:
        pass

    pygame.mixer.quit()  


    os.remove("sound2.mp3")


def play_audio_file(fname=DETECT_DONG):
    """Simple callback function to play a wave file. By default it plays
    a Ding sound.

    :param str fname: wave file name
    :return: None
    """
    ding_wav = wave.open(fname, 'rb')
    ding_data = ding_wav.readframes(ding_wav.getnframes())
    # with no_alsa_error():
    audio = pyaudio.PyAudio()
    stream_out = audio.open(
        format=audio.get_format_from_width(ding_wav.getsampwidth()),
        channels=ding_wav.getnchannels(),
        rate=ding_wav.getframerate(), input=False, output=True)
    stream_out.start_stream()
    stream_out.write(ding_data)
    time.sleep(0.2)
    stream_out.stop_stream()
    stream_out.close()
    audio.terminate()