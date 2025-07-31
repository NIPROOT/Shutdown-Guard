import os
import platform
import time
import datetime
import pyttsx3 
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def check_os():
    try:
        return platform.system()  
    except Exception as ex:
        print("Error detecting OS:", ex)
        return None


def eamil_alert():
    try:
        with open("email_settings.txt", 'r') as f:
            info = f.readlines()
            f.close()


        sender_email = info[0].replace("\n","")

        sender_app_password = info[1].replace("\n","")
    
        reciver_email = info[2].replace("\n","")

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["subject"] = "Warning: Your power is about to go out!!"
        msg["To"] = reciver_email
        msg.attach(MIMEText("Warning: Your power is about to go out. Please turn it off as soon as possible to protect your computer.", "plain"))

        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(sender_email, sender_app_password)
        s.send_message(msg)
    except Exception as e:
        print("Error:", e)




def Warning_alert():
    try:
        eamil_alert()
        pyttsx3.speak("Alert You Time Has Been Ended")
        pyttsx3.speak("Please Save your project and files")
        pyttsx3.speak("And shutdown your pc")
        time.sleep(5)
        pyttsx3.speak("Alert You Time Has Been Ended")
        pyttsx3.speak("Please Save your project and files")
        pyttsx3.speak("And shutdown your pc")
        eamil_alert()
        time.sleep(5)
    except Exception as e:
        print("Error:", e)






def get_time_off():
    try:
            pyttsx3.speak("alert turn off system in")
            eamil_alert()
            pyttsx3.speak("5")
            pyttsx3.speak("4")
            pyttsx3.speak("3")
            pyttsx3.speak("2")
            pyttsx3.speak("1")
            turn_off_system()

    except Exception as e:
        print("Error:", e)


def turn_off_system():
    try:
        os_name = check_os()
        if not os_name:
            print("Cannot detect operating system.")
            return

        os_name = os_name.lower()

        if os_name == "windows":
            print("Shutting down Windows...")
            os.system("shutdown /s /t 0")
        elif os_name == "linux":
            print("Shutting down Linux...")
            os.system("shutdown -h now")
        elif os_name == "darwin":
            print("Shutting down macOS...")
            os.system("sudo shutdown -h now")
        else:
            print(f"Unsupported OS: {os_name}")
    except Exception as e:
        print("Error shutting down:", e)


def check_time():
    try:
        with open("shutdown_time.txt", 'r') as f:
            info = f.readlines()
            
        time_alert = str(info[0])
        hour_alert, min_alert = map(int, time_alert.split(":"))
        time.sleep(15)
        while True:
            now = datetime.datetime.now()
            curret_hour = now.hour
            curret_min = now.minute
            curret_total_min = curret_hour * 60 + curret_min
            alert_total_min = hour_alert * 60 + min_alert
            if curret_total_min == alert_total_min:
                get_time_off()
                break
            elif alert_total_min - curret_total_min == 5:
                Warning_alert()
                time.sleep(15)
                continue
            else:
                time.sleep(15)
                continue
    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    check_time()