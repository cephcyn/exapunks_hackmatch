from skimage.metrics import structural_similarity
import cv2
import numpy as np


# Extract game panel given a prev- and post- screenshots
# The game panel data is from the post- screenshot
# Reference https://stackoverflow.com/a/56193442
def extract_panel(im_prev, im_post):
    im_prev = cv2.imread(im_prev)
    im_post = cv2.imread(im_post)

    # convert to greyscale
    im_prev_grey = cv2.cvtColor(im_prev, cv2.COLOR_BGR2GRAY)
    im_post_grey = cv2.cvtColor(im_post, cv2.COLOR_BGR2GRAY)

    # compute SSIM
    score, diff = structural_similarity(im_prev_grey, im_post_grey, full=True)

    # scale diff from [0,1] to [0,255] to enable use with OpenCV
    diff = (diff * 255).astype('uint8')

    # threshold the diff image
    thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    # calculate diff contour regions
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    #panels = im_post.copy()

    # get the largest diff zone, thats almost certainly game panel
    area_max = 0
    x_max = 0
    y_max = 0
    w_max = 0
    for c in contours:
        area = cv2.contourArea(c)
        if area > 40:
            x, y, w, h = cv2.boundingRect(c)
            #cv2.rectangle(panels, (x, y), (x + w, y + h), (0, 255, 0), 3)
            if area > area_max:
                area_max = area
                x_max = x
                y_max = y
                w_max = w

    # extract the game panel and return its image data
    h_max = int(w_max * 1.5) # the game panel ratio is pretty consistent?
    return im_post[y_max:y_max+h_max, x_max:x_max+w_max].copy()


def identify_block(im, ref_block_types):
    score_1 = -1
    block_1 = ''
    score_2 = -1
    block_2 = ''
    for ref_block in ref_block_types:
        ref_match = cv2.matchTemplate(
                im,
                ref_block[2],
                cv2.TM_CCOEFF_NORMED
        )
        ref_score = ref_match[0][0]
        if ref_score > score_1:
            score_2 = score_1
            block_2 = block_1
            score_1 = ref_score
            block_1 = ref_block[1]
        elif ref_score > score_2:
            score_2 = ref_score
            block_2 = ref_block[1]
    if score_1 > 0.4:
        return block_1
    return 'none'


def read_state(im_prev, im_post, im_draw):
    im_game = extract_panel(im_prev, im_post)
    #im_game_grey = cv2.cvtColor(im_game, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(im_draw, im_game)

    # calculate the size of block in pixels
    block_size = im_game.shape # returns (height,width,channelcount)
    block_size = block_size[1] # only extract width
    block_size = block_size * (420/425) # cut off extra pixels
    block_size = int(block_size/7) # there are 7 columns in a game

    # Reference for block appearance
    # Each element is (ref-filename, color_shape identifier)
    ref_block_types = [
            ('ref/b_blu_grid.png', 'b_blu'),
            ('ref/b_grn_diam.png', 'b_grn'),
            ('ref/b_pnk_star.png', 'b_pnk'),
            ('ref/b_red_excl.png', 'b_red'),
            ('ref/b_ylw_rows.png', 'b_ylw'),
            ('ref/s_blu_grid.png', 's_blu'),
            ('ref/s_grn_diam.png', 's_grn'),
            ('ref/s_pnk_star.png', 's_pnk'),
            ('ref/s_red_excl.png', 's_red'),
            ('ref/s_ylw_rows.png', 's_ylw'),
    ]
    # Load in the cv2 reference image parses
    ref_block_types = [
            (i[0], i[1], cv2.imread(i[0]))
            for i in ref_block_types
    ]
    ref_block_types = [
            (i[0], i[1], cv2.resize(i[2], (block_size, block_size)))
            for i in ref_block_types
    ]

    # Search game panel space for the most-fitting block
    # Reference https://bits.mdminhazulhaque.io/opencv/find-image-in-another-image-using-opencv-and-numpy.html
    # Reference https://docs.opencv.org/3.4/d4/dc6/tutorial_py_template_matching.html
    p_max_val = 0
    p_max_loc = (0,0)
    for ref_block in ref_block_types:
        ref_match = cv2.matchTemplate(
                im_game,
                ref_block[2],
                cv2.TM_CCOEFF_NORMED
        )
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(ref_match)
        if max_val > p_max_val:
            p_max_val = max_val
            p_max_loc = max_loc
        #ref_match = (ref_match * 255).astype('uint8')
        #cv2.imwrite(f'test-{ref_block[1]}.png', ref_match)

    # Figure out the pin position of that most-fitting block
    p_max_pos = (int(p_max_loc[0]/block_size), int(p_max_loc[1]/block_size))

    # Process each individual block position now
    board_dims = (7, 10)
    board = [[] for i in range(board_dims[0])]
    for i_x in range(board_dims[0]):
        for i_y in range(board_dims[1]):
            loc_curr = (
                    p_max_loc[0] + (i_x - p_max_pos[0])*block_size,
                    p_max_loc[1] + (i_y - p_max_pos[1])*block_size
            )
            im_game_xy = im_game[loc_curr[1]:loc_curr[1]+block_size, loc_curr[0]:loc_curr[0]+block_size]
            tag = identify_block(im_game_xy, ref_block_types)
            #cv2.imwrite(f'out-{i_x}-{i_y}-{tag}.png', im_game_xy)
            #print(i_x, i_y, loc_curr, tag)
            board[i_x].append(tag)
    
    # Figure out where the drone currently is
    cpos = 3
    cpos_score = -1
    im_bot = cv2.imread('ref/x_bot.png')
    im_bot = cv2.resize(im_bot, (block_size, block_size))
    for i_x in range(board_dims[0]):
        i_y = 9
        loc_curr = (
                p_max_loc[0] + (i_x - p_max_pos[0])*block_size,
                p_max_loc[1] + (i_y - p_max_pos[1])*block_size
        )
        im_game_xy = im_game[loc_curr[1]:loc_curr[1]+block_size, loc_curr[0]:loc_curr[0]+block_size]
        ref_match = cv2.matchTemplate(
                im_game_xy,
                im_bot,
                cv2.TM_CCOEFF_NORMED
        )
        tpos_score = ref_match[0][0]
        if tpos_score>cpos_score:
            cpos = i_x
            cpos_score = tpos_score
    return board, cpos

