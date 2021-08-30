from skimage.metrics import structural_similarity
import cv2
import numpy as np

# Reference for block colors
# Each element is (BGR, color, shape)
BLOCKREF = [
        ((81, 89, 57), 'empty', 'empty'),
        ((147, 176, 18), 'green', 'diamond'),
        ((122, 52, 30), 'blue', 'grid'),
        ((49, 22, 218), 'red', 'excl'),
        ((188, 31, 253), 'pink', 'star'),
        ((25, 154, 222), 'yellow', 'rows'),
]

# Reference https://stackoverflow.com/a/56193442
def read_state(im_prev, im_post, im_draw):
    before = cv2.imread(im_prev)
    after = cv2.imread(im_post)
    
    # convert to greyscale
    before_grey = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
    after_grey = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)
    
    # compute SSIM
    (score, diff) = structural_similarity(before_grey, after_grey, full=True)
    #print('image similarity:', score)
    
    # scale diff from [0,1] to [0,255] to enable use with opencv
    diff = (diff * 255).astype('uint8')
    
    # Threshold the difference image, followed by finding contours to
    # obtain the regions of the two input images that differ
    thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    
    panels = after.copy()
    
    # get largest diff zone to find game panel
    area_max = 0
    x_max = 0
    y_max = 0
    w_max = 0
    h_max = 0
    for c in contours:
        area = cv2.contourArea(c)
        if area > 40:
            x,y,w,h = cv2.boundingRect(c)
            cv2.rectangle(panels, (x, y), (x + w, y + h), (0,255,0), 3)
            if (area > area_max):
                area_max = area
                x_max = x
                y_max = y
                w_max = w
                h_max = h
            #cv2.drawContours(mask, [c], 0, (0,255,0), -1)
            #cv2.drawContours(filled_after, [c], 0, (0,255,0), -1)
    # draw the game panel
    cv2.rectangle(
            panels, 
            (x_max, y_max), 
            (x_max + w_max, y_max + h_max), 
            (255, 0, 0), 
            3
    )
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
            print([(p[np.argmin(p)], BLOCKREF[np.argmin(p)][1]) for p in gdists])
            ideal = np.argmin(gdists)
            print(BLOCKREF[ideal%len(BLOCKREF)][1])

    cv2.imwrite(im_draw, panels)

