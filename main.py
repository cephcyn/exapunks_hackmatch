import time
import PIL.ImageGrab

import gameparser
import gamesolver

# force bot to leftmost position
moves = gamesolver.reset_pos()
print(moves)
# TODO actually do the moves

# get screenshot of game state
# ?Q: how does this interact with multi-monitor setup?
#im1 = PIL.ImageGrab.grab()
#im1.save('temp1.png')
#time.sleep(0.5)
#im2 = PIL.ImageGrab.grab()
#im2.save('temp2.png')

# parse screenshot of game state
state = gameparser.read_state('temp1.png', 'temp2.png', 'temp_panels.png')

# print game state
state_cols = len(state)
state_rows = len(state[0])
for r in range(state_rows):
    print(' '.join([c[r] if c[r]!='none' else '----------' for c in state]))

# decide which moves to make
soln = gamesolver.solve_state(state)
print(soln)

