#pyttsx3===>text to audio package
import pyttsx3
tex_sp=pyttsx3.init() #class
text=input("Enter a text:")

voices = tex_sp.getProperty('voices') #female
tex_sp.setProperty('voice',voices[1].id) 
tex_sp.setProperty('volume',1) #set volume  0-1
tex_sp.setProperty('rate', 200) #set voice speed

tex_sp.say(text)   #say=== function for convert text into audio
tex_sp.runAndWait() 