import gameviewer

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
#         ('pos', 0), # Move to c0
#         ('0move0', 1, 2), # 0deep grab from c1, 0deep drop in c2
#         ('1move0', 1, 2), # 1deep grab from c1, 0deep drop in c2
#         ('2move0', 1, 2), # 2deep grab from c1, 0deep drop in c2
#         ('1move1', 1, 2), # 1deep grab from c1, 1deep drop in c2
#         ('1move2', 1, 2), # 1deep grab from c1, 1deep drop in c2
#         ('2move2', 1, 2), # 2deep grab from c1, 2deep drop in c2
#         ('swap', 3), # Swap blocks in c3
#         ('deepswap', 4), # Deep pull (pick, swap, drop) in c4
#         ('deepshove', 4), # Deep push (swap, pick, swap, drop) in c4
# ]


def translate_to_keys(actions, cpos=-1):
    # Takes in an ACT_SEQUENCE format list and convert it to actions
    direct_actions = []

    # Handle auto current-position reset vs move handling
    def move_to(col, c_pos):
        moves = []
        if c_pos==-1:
            # If no current position guaranteed, force reset
            moves += ['m_left']*6
            moves += ['m_right']*col
            c_pos = col
        else:
            # If we know current position, move directly
            if c_pos>col:
                # Move leftwards
                moves += ['m_left']*(c_pos-col)
            else:
                # Move rightwards
                moves += ['m_right']*(col-c_pos)
            c_pos = col
        return c_pos, moves

    # Parse high-level actions into literal move commands
    for a in actions:
        if a[0]=='pos':
            # Move to col [1]
            cpos, nmoves = move_to(a[1], cpos)
            direct_actions += nmoves
        elif a[0]=='0move0':
            # 0deep grab from col [1], 0deep drop in col [2]
            cpos, nmoves = move_to(a[1], cpos)
            direct_actions += nmoves
            direct_actions += ['a_pickup']
            cpos, nmoves = move_to(a[2], cpos)
            direct_actions += nmoves
            direct_actions += ['a_pickup']
        elif a[0]=='1move0':
            # 1deep grab from col [1], 0deep drop in col [2]
            cpos, nmoves = move_to(a[1], cpos)
            direct_actions += nmoves
            direct_actions += ['a_swap']
            direct_actions += ['a_pickup']
            cpos, nmoves = move_to(a[2], cpos)
            direct_actions += nmoves
            direct_actions += ['a_pickup']
        elif a[0]=='2move0':
            # 2deep grab from col [1], 0deep drop in col [2]
            cpos, nmoves = move_to(a[1], cpos)
            direct_actions += nmoves
            direct_actions += ['a_pickup']
            direct_actions += ['a_swap']
            direct_actions += ['a_pickup']
            direct_actions += ['a_swap']
            direct_actions += ['a_pickup']
            cpos, nmoves = move_to(a[2], cpos)
            direct_actions += nmoves
            direct_actions += ['a_pickup']
        elif a[0]=='1move1':
            # 1deep grab from col [1], 1deep drop in col [2]
            cpos, nmoves = move_to(a[1], cpos)
            direct_actions += nmoves
            direct_actions += ['a_swap']
            direct_actions += ['a_pickup']
            cpos, nmoves = move_to(a[2], cpos)
            direct_actions += nmoves
            direct_actions += ['a_pickup']
            direct_actions += ['a_swap']
        elif a[0]=='1move2':
            # 1deep grab from col [1], 2deep drop in col [2]
            cpos, nmoves = move_to(a[1], cpos)
            direct_actions += nmoves
            direct_actions += ['a_swap']
            direct_actions += ['a_pickup']
            cpos, nmoves = move_to(a[2], cpos)
            direct_actions += nmoves
            direct_actions += ['a_pickup']
            direct_actions += ['a_swap']
            direct_actions += ['a_pickup']
            direct_actions += ['a_swap']
            direct_actions += ['a_pickup']
        elif a[0]=='2move2':
            # 2deep grab from col [1], 2deep drop in col [2]
            cpos, nmoves = move_to(a[1], cpos)
            direct_actions += nmoves
            direct_actions += ['a_pickup']
            direct_actions += ['a_swap']
            direct_actions += ['a_pickup']
            direct_actions += ['a_swap']
            direct_actions += ['a_pickup']
            cpos, nmoves = move_to(a[2], cpos)
            direct_actions += nmoves
            direct_actions += ['a_pickup']
            direct_actions += ['a_swap']
            direct_actions += ['a_pickup']
            direct_actions += ['a_swap']
            direct_actions += ['a_pickup']
        elif a[0]=='swap':
            #0deep swap blocks in col [1]
            cpos, nmoves = move_to(a[1], cpos)
            direct_actions += nmoves
            direct_actions += ['a_swap']
        elif a[0]=='deepswap':
            # 1deep swap blocks in col [1]
            cpos, nmoves = move_to(a[1], cpos)
            direct_actions += nmoves
            direct_actions += ['a_pickup']
            direct_actions += ['a_swap']
            direct_actions += ['a_pickup']
        elif a[0]=='deepshove':
            # 0->2 deep push blocks in col [1]
            cpos, nmoves = move_to(a[1], cpos)
            direct_actions += nmoves
            direct_actions += ['a_swap']
            direct_actions += ['a_pickup']
            direct_actions += ['a_swap']
            direct_actions += ['a_pickup']
    # Parse literal move commands into key inputs
    keys = [KEYMAP[i] for i in direct_actions]
    return keys


def move_complexity(a):
    if a[0]=='0move0':
        return 3 # abs(a[1]-a[2])
    elif a[0]=='1move0':
        return 3 # abs(a[1]-a[2])
    elif a[0]=='2move0':
        return 3 # abs(a[1]-a[2])
    elif a[0]=='1move1':
        return 3 # abs(a[1]-a[2])
    elif a[0]=='1move2':
        return 3 # abs(a[1]-a[2])
    elif a[0]=='2move2':
        return 3 # abs(a[1]-a[2])
    elif a[0]=='swap':
        return 1
    elif a[0]=='deepswap':
        return 1.1
    elif a[0]=='deepshove':
        return 1.1
    return 1


def state_collapse(state, clumps_idtoloc):
    new_state = [[b for b in c] for c in state]
    collapsed = False
    # return collapsed form of a state
    for id in [i for i in clumps_idtoloc if len(clumps_idtoloc[i])>=2]:
        block_type = clumps_idtoloc[id][0]
        block_type = state[block_type[0]][block_type[1]]
        if block_type[0]=='s':
            # if this is spikes, remove the clump of spikes
            for loc in clumps_idtoloc[id]:
                new_state[loc[0]][loc[1]] = 'EMPTY'
            # And then remove all the relevant blocks matching color
            for i_c in range(len(new_state)):
                for i_r in range(len(new_state[i_c])):
                    if new_state[i_c][i_r]==block_type:
                        new_state[i_c][i_r] = 'EMPTY'
            collapsed = True
        elif block_type[0]=='b' and len(clumps_idtoloc[id])>=4:
            # if this is blocks, remove the clump of blocks
            for loc in clumps_idtoloc[id]:
                new_state[loc[0]][loc[1]] = 'EMPTY'
            collapsed = True
    # Make all blocks fall back
    for i_c in range(len(new_state)):
        new_state[i_c] = [i for i in new_state[i_c] if i!='EMPTY']
    # Now try to compute the new matchings, if any
    if collapsed:
        _, new_state = state_matched(new_state)
    return new_state


def state_matched(state):
    # return true, nextstate iff state will result in a match
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
                    if merged and above_id!=left_id:
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
        len(set(i))>=4
        for i in clumps_idtoloc.values()
    ])
    spike_possible = any([
        len(set(i))>=2 and state[i[0][0]][i[0][1]][0]=='s'
        for i in clumps_idtoloc.values()
    ])
    return (block_possible or spike_possible), \
            state_collapse(state, clumps_idtoloc)


def state_modify(state, action, cpos):
    # check if possible
    if action[0]=='0move0' and \
            len(state[action[1]])<1:
        return False, cpos
    if action[0]=='1move0' and \
            len(state[action[1]])<2:
        return False, cpos
    if action[0]=='2move0' and \
            len(state[action[1]])<3:
        return False, cpos
    if action[0]=='1move1' and \
            (len(state[action[1]])<2 or len(state[action[2]])<1):
        return False, cpos
    if action[0]=='1move2' and \
            (len(state[action[1]])<2 or len(state[action[2]])<2):
        return False, cpos
    if action[0]=='2move2' and \
            (len(state[action[1]])<3 or len(state[action[2]])<2):
        return False, cpos
    if action[0]=='swap' and \
            len(state[action[1]])<2:
        return False, cpos
    if action[0]=='deepswap' and \
            len(state[action[1]])<3:
        return False, cpos
    if action[0]=='deepshove' and \
            len(state[action[1]])<3:
        return False, cpos

    # check if it will result in a reasonable change
    if action[0]=='swap' and state[action[1]][-1]==state[action[1]][-2]:
        return False, cpos
    if action[0]=='deepswap' and state[action[1]][-2]==state[action[1]][-3]:
        return False, cpos
    if action[0]=='deepshove' and state[action[1]][-1]==state[action[1]][-3]:
        return False, cpos

    # create modified state
    modified_state = []
    for i_c in range(len(state)):
        modified_state.append([])
        for i_r in range(len(state[i_c])):
            modified_state[i_c].append(state[i_c][i_r])
    # apply the move
    if action[0]=='0move0':
        block = state[action[1]][-1]
        modified_state[action[1]] = modified_state[action[1]][:-1]
        modified_state[action[2]] = modified_state[action[2]]+[block]
    if action[0]=='1move0':
        block = state[action[1]][-2]
        modified_state[action[1]] = modified_state[action[1]][:-2] \
                +[modified_state[action[1]][-1]]
        modified_state[action[2]] = modified_state[action[2]]+[block]
    if action[0]=='2move0':
        block = state[action[1]][-3]
        modified_state[action[1]] = modified_state[action[1]][:-3] \
                +[modified_state[action[1]][-2]] \
                +[modified_state[action[1]][-1]]
        modified_state[action[2]] = modified_state[action[2]]+[block]
    if action[0]=='1move1':
        block = state[action[1]][-2]
        modified_state[action[1]] = modified_state[action[1]][:-2] \
                +[modified_state[action[1]][-1]]
        modified_state[action[2]] = modified_state[action[2]][:-1] \
                +[block] \
                +[modified_state[action[2]][-1]]
    if action[0]=='1move2':
        block = state[action[1]][-2]
        modified_state[action[1]] = modified_state[action[1]][:-2] \
                +[modified_state[action[1]][-1]]
        modified_state[action[2]] = modified_state[action[2]][:-2] \
                +[block] \
                +[modified_state[action[2]][-2]] \
                +[modified_state[action[2]][-1]]
    if action[0]=='2move2':
        block = state[action[1]][-3]
        modified_state[action[1]] = modified_state[action[1]][:-3] \
                +[modified_state[action[1]][-2]] \
                +[modified_state[action[1]][-1]]
        modified_state[action[2]] = modified_state[action[2]][:-2] \
                +[block] \
                +[modified_state[action[2]][-2]] \
                +[modified_state[action[2]][-1]]
    if action[0]=='swap':
        modified_state[action[1]] = modified_state[action[1]][:-2] \
                +[modified_state[action[1]][-1]] \
                +[modified_state[action[1]][-2]]
    if action[0]=='deepswap':
        modified_state[action[1]] = modified_state[action[1]][:-3] \
                +[modified_state[action[1]][-2]] \
                +[modified_state[action[1]][-3]] \
                +[modified_state[action[1]][-1]]
    if action[0]=='deepshove':
        modified_state[action[1]] = modified_state[action[1]][:-3] \
                +[modified_state[action[1]][-1]] \
                +[modified_state[action[1]][-3]] \
                +[modified_state[action[1]][-2]]
    # check if exceeds height bound
    if any([len(c)>9 for c in modified_state]):
        return False, cpos
    return modified_state, action[-1]


def solve_state(state, cpos=-1):
    # Use BFS to find the easiest viable action

    # check if solve is even possible
    counts = {}
    for c in state:
        for b in c:
            if b not in counts:
                counts[b] = 0
            counts[b] += 1
    block_solvable = any([
        counts[t]>4 for t in counts
    ])
    spike_solvable = any([
        counts[t]>2 for t in counts if t[0]=='s'
    ])
    if not (block_solvable or spike_solvable):
        return [], [], state, cpos

    # set up moves to search at every step
    MOVESET = []
    for c_a in range(7):
        MOVESET.append( ('swap', c_a) )
        MOVESET.append( ('deepswap', c_a) )
        MOVESET.append( ('deepshove', c_a) )
    for c_a in range(7):
        for d_b in range(1,7):
            if c_a+d_b<7:
                MOVESET.append( ('0move0', c_a, c_a+d_b) )
                MOVESET.append( ('1move0', c_a, c_a+d_b) )
                MOVESET.append( ('2move0', c_a, c_a+d_b) )
                MOVESET.append( ('1move1', c_a, c_a+d_b) )
                MOVESET.append( ('1move2', c_a, c_a+d_b) )
                MOVESET.append( ('2move2', c_a, c_a+d_b) )
            if c_a-d_b>=0:
                MOVESET.append( ('0move0', c_a, c_a-d_b) )
                MOVESET.append( ('1move0', c_a, c_a-d_b) )
                MOVESET.append( ('2move0', c_a, c_a-d_b) )
                MOVESET.append( ('1move1', c_a, c_a-d_b) )
                MOVESET.append( ('1move2', c_a, c_a-d_b) )
                MOVESET.append( ('2move2', c_a, c_a-d_b) )

    # now do the actual bfs
    state_queue = [(a, [a], state, a[-1]) for a in MOVESET]
    new_state_queue = []
    max_steps = max([len(c) for c in state])*15
    steps = 0
    min_sq = ([], [], state, cpos)
    min_height = 11
    while len(state_queue)>0 and steps<max_steps:
        print(f'bfs step {steps}: begin')
        print(f'bfs step {steps}: queue len={len(state_queue)}')
        state_queue = sorted(
                state_queue,
                key=lambda x: sum([
                    move_complexity(c) for c in x[1]
                ])
        )
        new_state_queue = []
        for sq in state_queue:
            state_step, cpos_step = state_modify(sq[2], sq[0], cpos=cpos)
            if state_step: # will be False if impossible
                matched, next_state = state_matched(state_step)
                if matched:
                    seq = translate_to_keys(sq[1], cpos=cpos)
                    hex_seq = [HEX_KEYMAP[i] for i in seq]
                    return sq[1], hex_seq, next_state, cpos_step
                else:
                    new_state_queue += [
                            (a, sq[1]+[a], next_state, cpos_step)
                            for a in MOVESET
                    ]
                state_height = max([len(c) for c in sq[2]])
                if state_height<min_height:
                    min_sq = sq
                    min_height = state_height
        steps += 1
        state_queue = new_state_queue
    seq = translate_to_keys(min_sq[1], cpos=cpos)
    hex_seq = [HEX_KEYMAP[i] for i in seq]
    return min_sq[1], hex_seq, min_sq[2], min_sq[3]
