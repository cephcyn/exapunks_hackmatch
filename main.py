import time
import PIL.ImageGrab

import gameparser
import gamesolver
import gameinput
import gameviewer

cpos = 3
im1 = PIL.ImageGrab.grab()
im1.save('sc_0.png')
time.sleep(0.3)
while True:
    # get screenshot of game state
    # ?Q: how does this interact with multi-monitor setup?
    im2 = PIL.ImageGrab.grab()
    im2.save('sc_1.png')

    # parse screenshot of game state
    state, cpos_temp = gameparser.read_state(
            'sc_0.png',
            'sc_1.png',
            'sc_panel.png'
    )
    print('present state:')
    gameviewer.print_state(state, cpos)

    # decide which moves to make
    soln, soln_hex, next_state, cpos = gamesolver.solve_state(state, cpos=cpos)
    print('soln:', soln, flush=True)
    print('soln_hex:', soln_hex, flush=True)
    print('targetd state:')
    gameviewer.print_state(next_state, cpos)
    print()

    # actually do the moves
    if len(soln_hex)>0:
        # there is a viable solution, execute it
        for k in soln_hex:
            gameinput.PressKey(k)
            time.sleep(0.03)
            gameinput.ReleaseKey(k)
            time.sleep(0.08)
        # wait for moves to time out
        time.sleep(0.5)
