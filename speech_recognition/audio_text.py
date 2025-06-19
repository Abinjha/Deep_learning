#pyaudio
#SpeechRecognition

import speech_recognition as sr

def speech_text():
    r=sr.Recognizer()   #to recongnize voice

    while True:
        with sr.Microphone() as source :  # same as source=microphone()
            print("speak")
            audio=r.listen(source)
            try:
                text=r.recognize_google(audio)
                print("you said",text)
            except:
                print("Did not hear any thing,please repeat")
speech_text()





