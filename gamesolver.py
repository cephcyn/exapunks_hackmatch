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
    # move to far left
    actions = ['m_left']*6
    # move to center
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
    # return true iff state will result in a match
    # Assumes input state is filtered already
    clumps_loctoid = {} # map {(c,r):id}
    clumps_idtoloc = {} # map {id:[(c,r)...]}
    ckpt_id = 0
    for i_c in range(len(state)):
        for i_r in range(len(state[i_c])):
            if i_c==0 and i_r==0:
                # if in corner, auto new clump
                clumps_loctoid[(i_c,i_r)] = ckpt_id
                clumps_idtoloc[ckpt_id] = [(i_c,i_r)]
                ckpt_id += 1
            else:
                merged = False
                above_id = -1
                if i_r!=0 and state[i_c][i_r]==state[i_c][i_r-1]:
                    # merge with above clump
                    above_id = clumps_loctoid[(i_c,i_r-1)]
                    clumps_loctoid[(i_c,i_r)] = above_id
                    clumps_idtoloc[above_id].append( (i_c,i_r) )
                    merged = True
                if i_c!=0 and len(state[i_c-1])>i_r and state[i_c][i_r]==state[i_c-1][i_r]:
                    # merge with leftwards clump
                    left_id = clumps_loctoid[(i_c-1,i_r)]
                    clumps_loctoid[(i_c,i_r)] = left_id
                    clumps_idtoloc[left_id].append( (i_c,i_r) )
                    if merged:
                        # need to combine the left and above clumps
                        # do this by setting the entire above clump to left_id
                        for above_loc in clumps_idtoloc[above_id]:
                            clumps_loctoid[above_loc] = left_id
                            clumps_idtoloc[left_id].append(above_loc)
                        clumps_idtoloc[above_id] = []
                    merged = True
                if not merged:
                    # no merge possible
                    clumps_loctoid[(i_c,i_r)] = ckpt_id
                    clumps_idtoloc[ckpt_id] = [(i_c,i_r)]
                    ckpt_id += 1
    return any([len(clumps_idtoloc[i])>=4 for i in clumps_idtoloc])


def solve_state(state):
    # Do spikes if possible
    # Otherwise use BFS to find the easiest viable action
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

    # If spikes are possible (at top-3 accessible), use them
    spikes = [s for s in top3 if (sum(top3[s])>2) and (s[0]=='s')]
    if len(spikes)>0:
        print('spikes possible')
        # TODO
    else:
        print('spikes impossible')

    # Otherwise, do BFS
    # TODO
    print(state_matched(state))
    return []
