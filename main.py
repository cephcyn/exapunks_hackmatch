import time
import PIL.ImageGrab

import gameparser

# get screenshot of game state
# ?Q: how does this interact with multi-monitor setup?
#im1 = PIL.ImageGrab.grab()
#im1.save('temp1.png')
#time.sleep(2)
#im2 = PIL.ImageGrab.grab()
#im2.save('temp2.png')

# parse screenshot of game state
gameparser.read_state('temp1.png', 'temp2.png', 'temp_panels.png')
