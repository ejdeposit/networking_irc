
from playsound import playsound as ps

sound = '/Users/charlesbolton/Desktop/594_Networking/networking_irc/'

def login():
   
   in_sound = sound+'login_tone.wav' 
   ps(in_sound)

def logout():
   
   out_sound = sound+'logout_tone.wav' 
   ps(out_sound)

def join():
   
   join_sound = sound+'join_tone.wav'
   ps(join_sound)
