
from playsound import playsound as ps

sound = '/Users/charlesbolton/Desktop/594_Networking/networking_irc/'

def login():
   
   in_sound = sound+'login_tone.wav' 
   ps(in_sound)

def logout():
   
   out_sound = sound+'logout_tone.wav' 
   ps(out_sound)

def create():
    
   create_sound = sound+'create_tone.wav'
   ps(create_sound)

def join():
   
   join_sound = sound+'join_tone.wav'
   ps(join_sound)

def switch():

    switch_sound = sound+'switch_tone.wav'
    ps(switch_sound)

def leave(): 
    
    leave_sound = sound+'leave_tone.wav'
    ps(leave_sound)

def message():

    message_sound = sound+'message_tone.wav'
    ps(message_sound)
