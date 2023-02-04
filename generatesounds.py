import pyttsx3
import json

settingsfile = open('soundsettings.json')
settings = json.load(settingsfile)

classes = settings['classes']

engine = pyttsx3.init()
engine.setProperty("rate", settings['speakingrate'])



for x in classes:
    engine.save_to_file(x, "./sounds/"+str(x)+".mp3")
    engine.runAndWait()
