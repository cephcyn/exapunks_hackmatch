import time
import PIL.ImageGrab

# get screenshot of game state
# ?Q: how does this interact with multi-monitor setup?
im1 = PIL.ImageGrab.grab()
im1.save('temp1.png')
#im1.show()
time.sleep(2)
im2 = PIL.ImageGrab.grab()
im2.save('temp2.png')

# parse screenshot of game state
