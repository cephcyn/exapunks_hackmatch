import time
import PIL.ImageGrab

import gameparser
import gamesolver
import gameinput


def print_state(state, cpos=-1):
    # print game state
    state_cols = len(state)
    state_rows = 10
    for r in range(state_rows):
        print(' '.join([
            c[r] if (len(c)>r) and (c[r]!='none') else '-----' 
            for c in state
        ]), flush=True)
    if cpos!=-1:
        print(' '.join(
            ['-----' for i in range(cpos)]+
            ['^^^^^']+
            ['-----' for i in range(state_cols-cpos-1)]))

cpos = 3
while True:
    # get screenshot of game state
    # ?Q: how does this interact with multi-monitor setup?
    im1 = PIL.ImageGrab.grab()
    im1.save('temp1.png')
    time.sleep(0.15)
    im2 = PIL.ImageGrab.grab()
    im2.save('temp2.png')

    # parse screenshot of game state
    state, cpos_temp = gameparser.read_state(
            'temp1.png', 'temp2.png', 'temp_panels.png'
    )
    print_state(state, cpos)

    # decide which moves to make
    soln, soln_hex, next_state, cpos = gamesolver.solve_state(state, cpos=cpos)
    print_state(next_state, cpos)
    print('soln:', soln, flush=True)
    print()
    print()

    # actually do the moves
    for k in soln_hex:
        gameinput.PressKey(k)
        time.sleep(0.02)
        gameinput.ReleaseKey(k)
        time.sleep(0.03)

    # wait for moves to time out
    time.sleep(0.15)

