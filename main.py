import time
import PIL.ImageGrab

import gameparser
import gamesolver
import gameinput


def print_state(state):
    # print game state
    state_cols = len(state)
    state_rows = 10
    for r in range(state_rows):
        print(' '.join([
            c[r] if (len(c)>r) and (c[r]!='none') else '----------' 
            for c in state
        ]))


while True:
    # get screenshot of game state
    # ?Q: how does this interact with multi-monitor setup?
    im1 = PIL.ImageGrab.grab()
    im1.save('temp1.png')
    time.sleep(0.5)
    im2 = PIL.ImageGrab.grab()
    im2.save('temp2.png')

    # parse screenshot of game state
    state = gameparser.read_state('temp1.png', 'temp2.png', 'temp_panels.png')
    print_state(state)

    # decide which moves to make
    soln, soln_hex, next_state = gamesolver.solve_state(state)
    print_state(next_state)
    print(soln, flush=True)
    print()
    print()

    # actually do the moves
    for k in soln_hex:
        gameinput.PressKey(k)
        time.sleep(0.01)
        gameinput.ReleaseKey(k)
        time.sleep(0.05)

