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
    h_max = int(w_max * 1.6) # the game panel ratio is pretty consistent?
    return im_post[y_max:y_max+h_max, x_max:x_max+w_max].copy()


def identify_block(im, ref_block_types):
    # TODO
    return 'blue'


def read_state(im_prev, im_post, im_draw):
    im_game = extract_panel(im_prev, im_post)
    im_game_grey = cv2.cvtColor(im_game, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(im_draw, im_game)

    # calculate the size of block in pixels
    block_size = im_game.shape # returns (height,width,channelcount)
    block_size = block_size[1] # only extract width
    block_size = block_size * (420/425) # cut off extra pixels
    block_size = int(block_size/7) # there are 7 columns in a game

    # Reference for block appearance
    # Each element is (ref-filename, color, shape)
    ref_block_types = [
            ('ref/block_green.png', 'green', 'diamond'),
            ('ref/block_blue.png', 'blue', 'grid'),
            ('ref/block_red.png', 'red', 'excl'),
            ('ref/block_pink.png', 'pink', 'star'),
            ('ref/block_yellow.png', 'yellow', 'rows'),
            ('ref/spike_green.png', 'green_spike', 'diamond_spike'),
            ('ref/spike_blue.png', 'blue_spike', 'grid_spike'),
            ('ref/spike_red.png', 'red_spike', 'excl_spike'),
            ('ref/spike_pink.png', 'pink_spike', 'star_spike'),
            ('ref/spike_yellow.png', 'yellow_spike', 'rows_spike'),
    ]

    # Search game panel space for the most-fitting block
    # Reference https://bits.mdminhazulhaque.io/opencv/find-image-in-another-image-using-opencv-and-numpy.html
    # Reference https://docs.opencv.org/3.4/d4/dc6/tutorial_py_template_matching.html
    p_max_val = 0
    p_max_loc = (0,0)
    for ref_block in ref_block_types:
        im_ref = cv2.imread(ref_block[0])
        im_ref = cv2.resize(im_ref, (int(block_size), int(block_size)))
        im_ref_grey = cv2.cvtColor(im_ref, cv2.COLOR_BGR2GRAY)
        ref_match = cv2.matchTemplate(
                im_game,
                im_ref,
                cv2.TM_CCOEFF_NORMED
        )
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(ref_match)
        if max_val > p_max_val:
            p_max_val = max_val
            p_max_loc = max_loc
        ref_match = (ref_match * 255).astype('uint8')
        cv2.imwrite(f'test-{ref_block[1]}.png', ref_match)

    # Figure out the pin position of that most-fitting block
    p_max_pos = (int(p_max_loc[0]/block_size), int(p_max_loc[1]/block_size))
    for i_x in range(7):
        for i_y in range(11):
            loc_curr = (
                    p_max_loc[0] + (i_x - p_max_pos[0])*block_size,
                    p_max_loc[1] + (i_y - p_max_pos[1])*block_size
            )
            im_game_xy = im_game[loc_curr[1]:loc_curr[1]+block_size, loc_curr[0]:loc_curr[0]+block_size]
            tag = identify_block(im_game_xy, ref_block_types)
            print(i_x, i_y, loc_curr, tag)
    # TODO

    """
    #print(h_max / (w_max / 7))
    # draw and identify game blocks
    for col in range(7):
        for row in range(9):
            sample_x_lo = x_max + int(w_max*col/7) + int(0.05*w_max/7)
            sample_x_hi = sample_x_lo + int(0.95*w_max/7)
            sample_y_lo = y_max + int(w_max*row/7)
            sample_y_hi = sample_y_lo + int(0.6*w_max/7)
            # draw block sample pane
            cv2.rectangle(
                    panels,
                    (sample_x_lo, sample_y_lo),
                    (sample_x_hi, sample_y_hi),
                    (0,0,255),
                    3
            )
            # average colors within block sample pane
            sample = after[sample_y_lo:sample_y_hi, sample_x_lo:sample_x_hi]
            block_color = cv2.mean(sample)
            cv2.rectangle(
                    panels,
                    (sample_x_lo, sample_y_lo),
                    (sample_x_hi, sample_y_hi),
                    block_color,
                    3
            )
            # k-means colors within block sample pane
            kmeans_num = 2
            sample_pixels = np.float32(sample.reshape(-1, 3))
            _, labels, palette = cv2.kmeans(
                    sample_pixels,
                    kmeans_num, # number of color groups
                    None, # 'bestLabels'
                    (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1), # criteria
                    10,
                    cv2.KMEANS_RANDOM_CENTERS # 'flags'
            )
            _, counts = np.unique(labels, return_counts=True)
            # draw each color group
            for i in range(kmeans_num):
                gcolor = palette[i] #palette[np.argmax(counts)]
                gcolor = (int(gcolor[0]), int(gcolor[1]), int(gcolor[2]))
                cv2.rectangle(
                        panels,
                        (sample_x_lo, sample_y_hi-(kmeans_num-i)*10),
                        (sample_x_hi, sample_y_hi-(kmeans_num-i-1)*10),
                        gcolor,
                        -1
                )
            # calculate color group dists
            gdists = [[sum(abs(p - r[0])) for r in BLOCKREF] for p in palette]
            ideal = np.argmin(gdists)
            print(
                    BLOCKREF[ideal%len(BLOCKREF)][1],
                    [(p[np.argmin(p)], BLOCKREF[np.argmin(p)][1]) for p in gdists]
            )

    cv2.imwrite(im_draw, im_game)
    """

