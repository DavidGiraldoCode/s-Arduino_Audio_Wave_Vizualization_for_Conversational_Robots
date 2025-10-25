add_library('serial')

#Import Processing libraries

# Declare globals
soundfiel = None;
serial_port = None;
display_message = ""
rgb = [0, 0, 0]
furhat_state = 's'
furhat_talking_state = 't'
furhat_listening_state = 's'

def setup():
    size(200, 200)
    
def draw():
    background(255 * random(0,1))
    
