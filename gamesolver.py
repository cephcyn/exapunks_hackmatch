# Default key-mapping of legal actions:
KEYMAP = {
        'm_left': 'a',
        'm_right': 'd',
        'a_pickup': 'j',
        'a_swap': 'k',
        'a_speedup': 'l', # this one should never be helpful to greedy bot...
}
# Reference https://gist.github.com/dretax/fe37b8baf55bc30e9d63
HEX_KEYMAP = {
        'a': 0x1E,
        'd': 0x20,
        'j': 0x24,
        'k': 0x25,
        'l': 0x26,
}

# # An example of an action seq
# ACT_SEQUENCE = [
#         ('pos', 0), # Move to col 0
#         ('pickup', 1, 2), # Pick up from col 1 and drop in col 2
#         ('swap', 3), # Swap blocks in col 3
#         ('deepswap', 4), # Deep swap (pick, swap, drop) in col 4
# ]


def translate_to_keys(actions):
    # Takes in an ACT_SEQUENCE format list and convert it to actions
    current_pos = -1
    direct_actions = []
    
    # Handle auto current-position reset vs move handling
    def move_to(col, cpos):
        moves = []
        if cpos==-1:
            # If no current position guaranteed, force reset
            moves += ['m_left']*6
            moves += ['m_right']*col
            cpos = col
        else:
            # If we know current position, move directly
            if cpos<col:
                # Move leftwards
                moves += ['m_left']*(cpos-col)
            else:
                # Move rightwards
                moves += ['m_right']*(col-cpos)
            cpos = col
        return cpos, moves

    # Parse high-level actions into literal move commands
    for a in actions:
        if a[0]=='pos':
            # Move to col [1]
            current_pos, nmoves = move_to(a[1], current_pos)
            direct_actions += nmoves
        elif a[0]=='pickup':
            # Pick up from col [1] and drop in col [2]
            current_pos, nmoves = move_to(a[1], current_pos)
            direct_actions += nmoves
            direct_actions += ['a_pickup']
            current_pos, nmoves = move_to(a[2], current_pos)
            direct_actions += nmoves
            direct_actions += ['a_pickup']
        elif a[0]=='swap':
            # Swap blocks in col [1]
            current_pos, nmoves = move_to(a[1], current_pos)
            direct_actions += nmoves
            direct_actions += ['a_swap']
        elif a[0]=='deepswap':
            # Deep-swap blocks in col [1]
            current_pos, nmoves = move_to(a[1], current_pos)
            direct_actions += nmoves
            direct_actions += ['a_pickup']
            direct_actions += ['a_swap']
            direct_actions += ['a_pickup']
    # Parse literal move commands into key inputs
    keys = [KEYMAP[i] for i in direct_actions]
    return keys


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
                if i_c!=0 \
                        and len(state[i_c-1])>i_r \
                        and state[i_c][i_r]==state[i_c-1][i_r]:
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
    block_possible = any([
        len(i)>=4 
        for i in clumps_idtoloc.values()
    ])
    spike_possible = any([
        len(i)>=2 
        for i in clumps_idtoloc.values() 
        if len(i)>0 and state[i[0][0]][i[0][1]][0]=='s'
    ])
    return block_possible or spike_possible


def state_modify(state, action):
    # check if possible
    if action[0]=='pickup' and len(state[action[1]])<1:
        return False
    if action[0]=='swap' and len(state[action[1]])<2:
        return False
    if action[0]=='deepswap' and len(state[action[1]])<3:
        return False

    # create modified state
    modified_state = []
    for i_c in range(len(state)):
        modified_state.append([])
        for i_r in range(len(state[i_c])):
            modified_state[i_c].append(state[i_c][i_r])
    # apply the move
    if action[0]=='pickup':
        block = state[action[1]][-1]
        modified_state[action[1]] = modified_state[action[1]][:-1]
        modified_state[action[2]] = modified_state[action[2]]+[block]
    if action[0]=='swap':
        modified_state[action[1]] = modified_state[action[1]][:-2] \
                +[modified_state[action[1]][-1]] \
                +[modified_state[action[1]][-2]]
    if action[0]=='deepswap':
        modified_state[action[1]] = modified_state[action[1]][:-3] \
                +[modified_state[action[1]][-2]] \
                +[modified_state[action[1]][-3]] \
                +[modified_state[action[1]][-1]]
    # check if exceeds height bound
    if any([len(c)>8 for c in modified_state]):
        return False
    return modified_state


def solve_state(state):
    # Use BFS to find the easiest viable action
    state = filter_state(state)

    # set up moves to search at every step
    MOVESET = []
    for c_a in range(7):
        MOVESET.append( ('swap', c_a) )
        MOVESET.append( ('deepswap', c_a) )
        for c_b in range(7):
            if c_a!=c_b:
                MOVESET.append( ('pickup', c_a, c_b) )

    # now do the actual bfs
    state_queue = [(a, [a], state) for a in MOVESET]
    new_state_queue = []
    max_steps = max([len(c) for c in state])
    max_steps = max_steps * max_steps
    steps = 0
    while len(state_queue)>0 and steps<max_steps:
        for sq in state_queue:
            state_step = state_modify(sq[2], sq[0])
            if state_step: # will be False if impossible
                if state_matched(state_step):
                    print(sq[1])
                    seq = translate_to_keys(sq[1])
                    hex_seq = [HEX_KEYMAP[i] for i in seq]
                    return seq, hex_seq, state_step
                else:
                    new_state_queue += [
                            (a, sq[1]+[a], state_step) 
                            for a in MOVESET
                    ]
        state_queue = new_state_queue
        steps += 1
    return [], [], state

