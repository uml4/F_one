import os
import speech_recognition as sr
import time
import sys
import ctypes
import wikipedia
import datetime
import json
import re
import webbrowser
import smtplib
import requests
import urllib
import urllib.request as urllib2
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pygame
import pyaudio
import wave
# from webdriver_manager.chrome import ChromeDriverManager
from time import strftime
from gtts import gTTS
from youtube_search import YoutubeSearch
import global_vars as g
import PCA9685 as PCA9685
import Common as Common
import board
import RPi.GPIO as GPIO
from thuvien.DetectObject import *
wikipedia.set_lang('vi')
# Create a dictionary called pins to store the pin number, name, and pin state:
pins = {
   18 : {'name' : 'GPIO 18', 'state' : GPIO.LOW},
   19 : {'name' : 'GPIO 19', 'state' : GPIO.LOW}
   }

# Set each pin as an output and make it low:
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

TOP_DIR = os.path.dirname(os.path.abspath(__file__))
DETECT_DING = os.path.join(TOP_DIR, "ding.wav")
DETECT_DONG = os.path.join(TOP_DIR, "dong.wav")

def speak(  text ):
    print("Bot: {}".format(text))
    tts = gTTS(text=text, lang='vi', slow=False)
    tts.save("sound.mp3")
    # playsound.playsound("sound.mp3")
    pygame.mixer.init()

    pygame.mixer.music.set_volume(1.0)


    pygame.mixer.music.load("sound.mp3")
    pygame.mixer.music.play()
    # os.remove("sound.mp3")

    while pygame.mixer.music.get_busy() == True:
        pass

    pygame.mixer.quit()  


    os.remove("sound.mp3")

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone(device_index=0) as source:
        print("Tôi: ", end='')
        audio = r.listen(source, phrase_time_limit=5)
        try:
            print(audio)
            print(r.recognize_google(audio,language='vi-VN',show_all=True))
            text = r.recognize_google(audio, language="vi-VN")
            print(text)
            return text
        # except:
        #     print("...")
        #     return 0
        except LookupError:
            print("Could not understand audio")	
            
        except sr.UnknownValueError:
            print("Try and Try Until You Die")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

def stop():
    speak("Hẹn gặp lại bạn sau!")



def get_text():
    for i in range(2):
        text = get_audio()
        if text:
            return text.lower()
        elif i < 2:
            speak("Bot không nghe rõ.")
    time.sleep(2)
    # stop()
    return 0

def get_hotword_text():

    text = get_audio()
    if text:
        return text.lower()
    # time.sleep(2)
    # stop()
    return 0

def hello(  name):
    day_time = int(strftime('%H'))
    if day_time < 12:
        speak("Chào buổi sáng bạn {}. Chúc bạn một ngày tốt lành.".format(name))
    elif 12 <= day_time < 18:
        speak("Chào buổi chiều bạn {}. Bạn đã dự định gì cho chiều nay chưa.".format(name))
    else:
        speak("Chào buổi tối bạn {}. Bạn đã ăn tối chưa nhỉ.".format(name))

def get_time(  text):
    now = datetime.datetime.now()
    if "giờ" in text:
        speak('Bây giờ là %d giờ %d phút' % (now.hour, now.minute))
    elif "ngày" in text:
        speak("Hôm nay là ngày %d tháng %d năm %d" %
            (now.day, now.month, now.year))
    else:
        speak("Bot chưa hiểu ý của bạn. Bạn nói lại được không?")


# Chỉ chạy khi nói 1 lệnh liên tục ví dụ nói: thời tiết ở đà năng là bao nhiêu
def current_weather():
    speak("Bạn muốn xem thời tiết ở đâu ạ.")
    ow_url = "http://api.openweathermap.org/data/2.5/weather?"
    city = get_text()
    if not city:
        pass
    api_key = "fe8d8c65cf345889139d8e545f57819a"
    call_url = ow_url + "appid=" + api_key + "&q=" + city + "&units=metric"
    response = requests.get(call_url)
    data = response.json()
    if data["cod"] != "404":
        city_res = data["main"]
        current_temperature = city_res["temp"]
        current_pressure = city_res["pressure"]
        current_humidity = city_res["humidity"]
        suntime = data["sys"]
        sunrise = datetime.datetime.fromtimestamp(suntime["sunrise"])
        sunset = datetime.datetime.fromtimestamp(suntime["sunset"])
        wthr = data["weather"]
        weather_description = wthr[0]["description"]
        now = datetime.datetime.now()
        content = """
        Hôm nay là ngày {day} tháng {month} năm {year}
        Mặt trời mọc vào {hourrise} giờ {minrise} phút
        Mặt trời lặn vào {hourset} giờ {minset} phút
        Nhiệt độ trung bình là {temp} độ C
        Áp suất không khí là {pressure} héc tơ Pascal
        Độ ẩm là {humidity}%
        Trời hôm nay quang mây. Dự báo mưa rải rác ở một số nơi.""".format(day = now.day,month = now.month, year= now.year, hourrise = sunrise.hour, minrise = sunrise.minute,
                                                                        hourset = sunset.hour, minset = sunset.minute, 
                                                                        temp = current_temperature, pressure = current_pressure, humidity = current_humidity)
        speak(content)
        time.sleep(20)
    else:
        speak("Không tìm thấy địa chỉ của bạn")

# Chỉ chạy khi nói 1 lệnh liên tục ví dụ nói: chơi nhạc bài con cò
def play_song():
    speak('Xin mời bạn chọn tên bài hát')
    mysong = get_text()
    while True:
        result = YoutubeSearch(mysong, max_results=10).to_dict()
        if result:
            break
    url = 'https://www.youtube.com' + result[0]['url_suffix']
    webbrowser.open(url)
    speak("Bài hát bạn yêu cầu đã được mở.")

def xoay_canh_tay_robot():
    huong_xoay = get_text()
    # global xoay_canh_tay
    # global xoay_canh_tay2
    # pwm = PCA9685()
    # pwm.setPWMFreq(50)
    if "trái" in huong_xoay:
        speak("qua trái")
        return 3
        # PCA9685.xoay_canh_tay = 3
    elif "phải" in huong_xoay:
        speak("qua phải")
        return 4
        # PCA9685.xoay_canh_tay = 4
    elif "trên" in huong_xoay:
        speak("nhìn lên")
        return 1
        # PCA9685.xoay_canh_tay = 1
    elif "dưới" in huong_xoay or "chào" in huong_xoay:
        speak("nhìn xuống")
        return 2
        # PCA9685.xoay_canh_tay = 2
    # print( "xoay_canh_tay_2 trong S"+ str(PCA9685.xoay_canh_tay) )

def tell_me_about():
    try:
        speak("Bạn muốn nghe về gì ạ")
        text = get_text()
        contents = wikipedia.summary(text).split('\n')
        speak(contents[0])
        time.sleep(10)
        for content in contents[1:]:
            speak("Bạn muốn nghe thêm không")
            ans = get_text()
            if "có" not in ans:
                break    
            speak(content)
            time.sleep(10)

        speak('Cảm ơn bạn đã lắng nghe!!!')
    except:
        speak("Bot không định nghĩa được thuật ngữ của bạn. Xin mời bạn nói lại")


def help_me():
    speak("""Bot có thể giúp bạn thực hiện các câu lệnh sau đây:
    1. Chào hỏi
    2. Hiển thị giờ
    3. Mở website, application
    4. Tìm kiếm trên Google
    5. Gửi email
    6. Dự báo thời tiết
    7. Mở video nhạc
    8. Thay đổi hình nền máy tính
    9. Đọc báo hôm nay
    10. Kể bạn biết về thế giới """)
    time.sleep(2)


def kt_phat_hien_hinhanh():
    return 1;

def play_audio_file(fname=DETECT_DING):
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


def assistant(  list_commands_p = None):
    list_commands = list_commands_p
    speak("Chào bạn ")
    while True:
        text = get_hotword_text()
        

        if not text:
            continue
        if "robot" in text:
            # chuông reo , đợi tối đa 5s
            play_audio_file()
            text = get_text()
            if not text:
                continue
            elif "dừng" in text or "tạm biệt" in text or "chào robot" in text or "ngủ thôi" in text:
                stop()
                pass
            elif "có thể làm gì" in text:
                help_me()
            elif "xin chào" in text:
                hello(name="Hoa")
            elif "mấy giờ" in text:
                get_time(text)
            elif "thời tiết" in text:
                current_weather()
            elif "chơi nhạc" in text:
                play_song()
                #  nên nói các câu có từ 3 từ trở lên ví dụ "hướng lên trên" "qua bên phải" 
            elif "bên phải" in text  or  "bên trái" in text or "hướng" in text or "robot chào" in text or "cúi chào" in text :
                list_commands['dk_canhtay_giongnoi'].value = xoay_canh_tay_robot()
            elif "ai đấy" in text or "ai thế" in text   or "chuyện gì" in text  or "gì vậy" in text  or "gì thế" in text:
                list_commands['dk_nhan_dien_hinhanh'].value = kt_phat_hien_hinhanh() 
                # dừng 2s để chụp hình
                time.sleep(2)
                # nếu "dk_nhan_dien_hinhanh": commands[1].value == 2 thì bắt đầu nhận diện và thông báo
                if not os.path.exists("need_to_detect.jpg"):
                    print(" Không tim thấy need_to_detect.jpg ")
                    speak("Không tìm thấy hình ảnh")
                    list_commands['dk_nhan_dien_hinhanh'].value = 0
                    
                else:
                    object_dict = detect_object("need_to_detect.jpg")
                    if not object_dict:
                        print ('empty dict')
                        speak("Không phát hiện bất thường")
                    else:
                        text = "Phát hiện "
                        for key in object_dict:
                            text = text + " " + str(object_dict[key]) +" " + str(key)
                        print (text)	
                        speak(text)
                        family_person_dict = detect_family_person( "need_to_detect.jpg" )
                        if  family_person_dict:
                            text2 = "Có vẻ là "
                            i = 0 
                            for key in family_person_dict:
                                if i == 0:								
                                    text2 = text2 + " " + str(key) 
                                else:
                                    text2 = text2 + " và  " + str(key) 	
                            print (text2)
                            speak(text2)	
                            

                    list_commands['dk_nhan_dien_hinhanh'].value = 0
                    os.remove("need_to_detect.jpg") 
                
                   
            elif "định nghĩa" in text:
                tell_me_about()
            elif "bật theo dõi" in text:
                    list_commands['tracking_object_status'].value = 1
                    speak('bật chế độ theo dõi')
            elif "tắt theo dõi" in text or "dừng theo dõi" in text:
                    list_commands['tracking_object_status'].value = 0    
                    speak('tắt chế độ theo dõi')    

            elif "bật đèn" in text:
                GPIO.output(18, GPIO.HIGH)
                speak('bật đèn')
            elif "tắt đèn" in text:
                GPIO.output(18, GPIO.LOW)    
                speak('tắt đèn')    

            else:
                speak("Bạn cần Bot giúp gì ạ?")

            play_audio_file(DETECT_DONG)
