import gameparser

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
            ['-----' for i in range(state_cols-cpos-1)]
        ), flush=True)
    else:
        print(' '.join(
            ['xxxxx' for i in range(state_cols)]
        ), flush=True)

def parse_state_string(input):
    # parse a game state string output into state form
    state = []
    cpos = -1
    lines = [l.strip() for l in input.split('\n') if len(l.strip())>0]
    # read in the input string block contents
    for line in lines[:-1]:
        blocks = line.strip().split(' ')
        state_cols = len(blocks)
        if len(state)==0:
            state = [[]]*state_cols
        for i_c in range(len(blocks)):
            state[i_c] = state[i_c] + [blocks[i_c]]
    # read the input string cpos contents
    cpos = -1
    lastline = lines[-1].split(' ')
    for i in range(len(lastline)):
        if lastline[i]=='^^^^^':
            cpos = i
            break
    return gameparser.filter_state(state), cpos
