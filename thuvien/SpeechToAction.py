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
# from webdriver_manager.chrome import ChromeDriverManager
from time import strftime
from gtts import gTTS
from youtube_search import YoutubeSearch
import global_vars as g
import PCA9685 as PCA9685
import Common as Common
import board
import RPi.GPIO as GPIO
wikipedia.set_lang('vi')
import wave


TOP_DIR = os.path.dirname(os.path.abspath(__file__))
DETECT_DING = os.path.join(TOP_DIR, "ding.wav")
DETECT_DONG = os.path.join(TOP_DIR, "dong.wav")
# Create a dictionary called pins to store the pin number, name, and pin state:
pins = {
   18 : {'name' : 'GPIO 18', 'state' : GPIO.LOW},
   19 : {'name' : 'GPIO 19', 'state' : GPIO.LOW}
   }

# Set each pin as an output and make it low:
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)


class SpeechToAction:
    def __init__(self,fname):
        self.fname = fname




    def speak(self, text):
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

    def get_audio(self):
        r = sr.Recognizer()
        # with sr.Microphone(device_index=0) as source:
        with sr.AudioFile(self.fname) as source:
            print("Tôi: ", end='')
            #audio = r.listen(source, phrase_time_limit=5)
            audio = r.record(source )  # read the entire audio file
            try:
                text = r.recognize_google(audio, language="vi-VN")
                print(text)
                return text
            except:
                print("...")
                return 0

    def stop(self):
        self.speak("Hẹn gặp lại bạn sau!")



    def get_text(self):
        # for i in range(3):
        text = self.get_audio()
        if text:
            return text.lower()
        else:                
            self.speak("Bot không nghe rõ!")
        # time.sleep(2)
        # self.stop()
        return 0

    def hello(self, name):
        day_time = int(strftime('%H'))
        if day_time < 12:
            self.speak("Chào buổi sáng bạn {}. Chúc bạn một ngày tốt lành.".format(name))
        elif 12 <= day_time < 18:
            self.speak("Chào buổi chiều bạn {}. Bạn đã dự định gì cho chiều nay chưa.".format(name))
        else:
            self.speak("Chào buổi tối bạn {}. Bạn đã ăn tối chưa nhỉ.".format(name))

    def get_time(self, text):
        now = datetime.datetime.now()
        if "giờ" in text:
            self.speak('Bây giờ là %d giờ %d phút' % (now.hour, now.minute))
        elif "ngày" in text:
            self.speak("Hôm nay là ngày %d tháng %d năm %d" %
                (now.day, now.month, now.year))
        else:
            self.speak("Bot chưa hiểu ý của bạn. Bạn nói lại được không?")


    # Chỉ chạy khi nói 1 lệnh liên tục ví dụ nói: thời tiết ở đà năng là bao nhiêu
    def current_weather(self):
        self.speak("Bạn muốn xem thời tiết ở đâu ạ.")
        ow_url = "http://api.openweathermap.org/data/2.5/weather?"
        city = self.get_text()
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
            self.speak(content)
            time.sleep(20)
        else:
            self.speak("Không tìm thấy địa chỉ của bạn")
    
    # Chỉ chạy khi nói 1 lệnh liên tục ví dụ nói: chơi nhạc bài con cò
    def play_song(self):
        self.speak('Xin mời bạn chọn tên bài hát')
        mysong = self.get_text()
        while True:
            result = YoutubeSearch(mysong, max_results=10).to_dict()
            if result:
                break
        url = 'https://www.youtube.com' + result[0]['url_suffix']
        webbrowser.open(url)
        self.speak("Bài hát bạn yêu cầu đã được mở.")

    def xoay_canh_tay_robot(self):
        huong_xoay = self.get_text()
        # global xoay_canh_tay
        # global xoay_canh_tay2
        # pwm = PCA9685()
        # pwm.setPWMFreq(50)
        if "trái" in huong_xoay:
            self.speak("qua trái")
            return 3
            # PCA9685.xoay_canh_tay = 3
        elif "phải" in huong_xoay:
            self.speak("qua phải")
            return 4
            # PCA9685.xoay_canh_tay = 4
        elif "trên" in huong_xoay:
            self.speak("nhìn lên")
            return 1
            # PCA9685.xoay_canh_tay = 1
        elif "dưới" in huong_xoay or "chào" in huong_xoay:
            self.speak("nhìn xuống")
            return 2
            # PCA9685.xoay_canh_tay = 2
        # print( "xoay_canh_tay_2 trong S"+ str(PCA9685.xoay_canh_tay) )

    def tell_me_about(self):
        try:
            self.speak("Bạn muốn nghe về gì ạ")
            text = self.get_text()
            contents = wikipedia.summary(text).split('\n')
            self.speak(contents[0])
            time.sleep(10)
            for content in contents[1:]:
                self.speak("Bạn muốn nghe thêm không")
                ans = get_text()
                if "có" not in ans:
                    break    
                self.speak(content)
                time.sleep(10)

            self.speak('Cảm ơn bạn đã lắng nghe!!!')
        except:
            self.speak("Bot không định nghĩa được thuật ngữ của bạn. Xin mời bạn nói lại")


    def help_me(self):
        self.speak("""Bot có thể giúp bạn thực hiện các câu lệnh sau đây:
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


    def kt_phat_hien_hinhanh(self):
        return 1;

    def play_audio_file(self, fname=DETECT_DONG):
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


    def assistant(self, list_commands_p = None):
        list_commands = list_commands_p
        self.speak("Chào bạn ")
        # while True:
        text = self.get_text()
        if not text:
            pass
        elif "dừng" in text or "tạm biệt" in text or "chào robot" in text or "ngủ thôi" in text:
            self.stop()
            pass
        elif "có thể làm gì" in text:
            self.help_me()
        elif "xin chào" in text:
            self.hello(name="Hoa")
        elif "mấy giờ" in text:
            self.get_time(text)
        elif "thời tiết" in text:
            self.current_weather()
        elif "chơi nhạc" in text:
            self.play_song()
            #  nên nói các câu có từ 3 từ trở lên ví dụ "hướng lên trên" "qua bên phải" 
        elif "bên phải" in text  or  "bên trái" in text or "hướng" in text or "robot chào" in text or "cúi chào" in text :
            list_commands['dk_canhtay_giongnoi'] = self.xoay_canh_tay_robot()
        elif "ai đấy" in text or "ai thế" in text   or "chuyện gì" in text  or "gì vậy" in text  or "gì thế" in text:
            list_commands['dk_nhan_dien_hinhanh'] = self.kt_phat_hien_hinhanh()    
        elif "định nghĩa" in text:
            self.tell_me_about()
        elif "bật theo dõi" in text:
                list_commands['tracking_object_status'] = 1
                self.speak('bật chế độ theo dõi')
        elif "tắt theo dõi" in text or "dừng theo dõi" in text:
                list_commands['tracking_object_status'] = 0    
                self.speak('tắt chế độ theo dõi')    

        elif "bật đèn" in text:
            GPIO.output(18, GPIO.HIGH)
            self.speak('bật đèn')
        elif "tắt đèn" in text:
            GPIO.output(18, GPIO.LOW)    
            self.speak('tắt đèn')    

        else:
            self.speak("Bạn cần Bot giúp gì ạ?")
            

        os.remove(self.fname) 
        return list_commands