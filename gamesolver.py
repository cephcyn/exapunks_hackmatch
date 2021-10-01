# Default key-mapping of legal actions:
KEYMAP = {
        'm_left': 'a',
        'm_right': 'd',
        'a_pickup': 'j',
        'a_swap': 'k',
        'a_speedup': 'l', # this one should never be helpful to greedy bot...
}


def translate_to_keys(actions):
    keys = [KEYMAP[i] for i in actions]
    return keys


def reset_pos():
    # move to the center of the board
    # there's 7 columns, and extra movement doesn't kill the bot
    # just move left 6 times
    actions = ['m_left']*6
    # then move to center
    actions += ['m_right']*3
    return translate_to_keys(actions)


def filter_state(state):
    # return state with ONLY filled column cells present
    state_out = [[] for i in range(len(state))]
    for i_c in range(len(state)):
        if 'none' in state[i_c]:
            state_out[i_c] = state[i_c][:state[i_c].index('none')]
        else:
            state_out[i_c] = state[i_c]
    return state_out


def state_matched(state):
    # TODO return true iff state will result in a match
    # Assumes input state is filtered already
    return False


def solve_state(state):
    # Use BFS to find the easiest viable action
    # Assumes that the controller is in the center already
    state = filter_state(state)

    # Count top3-blocks
    top3 = {
            'b_blu_grid': [0]*7,
            'b_grn_diam': [0]*7,
            'b_pnk_star': [0]*7,
            's_red_excl': [0]*7,
            's_ylw_rows': [0]*7,
            's_blu_grid': [0]*7,
            's_grn_diam': [0]*7,
            's_pnk_star': [0]*7,
            's_red_excl': [0]*7,
            's_ylw_rows': [0]*7,
    }
    for i_c in range(7):
        for s in state[i_c][-3:]:
            if s in top3:
                top3[s][i_c] += 1
    print(top3)

    # If spikes are possible (at top-3 accessible), use them
    spikes = [s for s in top3 if (sum(top3[s])>2) and (s[0]=='s')]
    print(spikes)
    if len(spikes)>0:
        print('spikes possible')
        # TODO

    # Otherwise, if single-col top3 move is possible, do it
    return []
