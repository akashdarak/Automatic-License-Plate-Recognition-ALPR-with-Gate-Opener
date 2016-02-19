import cv2
import numpy as np
import sys
import os.path

if len(sys.argv) != 3:
    print "%s input_file output_file" % (sys.argv[0])
    sys.exit()
else:
    input_file = sys.argv[1]
    output_file = sys.argv[2]

if not os.path.isfile(input_file):
    print "File not present '%s'" % input_file
    sys.exit()

DEBUG = 0

# Pixel intensity can be calculated as 0.30R + 0.59G + 0.11B
def ii(xx, yy):
    global img, img_y, img_x
    if yy >= img_y or xx >= img_x:
        return 0
    pixel = img[yy][xx]
    return 0.30 * pixel[2] + 0.59 * pixel[1] + 0.11 * pixel[0]


# contour check whether it is connected or not
def connected(contour):
    first = contour[0][0]
    last = contour[len(contour) - 1][0]
    return abs(first[0] - last[0]) <= 1 and abs(first[1] - last[1]) <= 1

def c(ind):
    global contours
    return contours[ind]



def count_child(ind, h_, contour):
    # Case when there is no child present
    if h_[ind][2] < 0:
        return 0
    else:
        if keep(c(h_[ind][2])):
            count = 1
        else:
            count = 0

            # No.of child's siblings
        count += count_siblings(h_[ind][2], h_, contour, True)
        return count


def is_child(ind, h_):
    return get_parent(ind, h_) > 0



def get_parent(ind, h_):
    parent = h_[ind][3]
    while not keep(c(parent)) and parent > 0:
        parent = h_[parent][3]

    return parent


def count_siblings(ind, h_, contour, inc_child=False):
    if inc_child:
        count = count_child(ind, h_, contour)
    else:
        count = 0

    
    p_ = h_[ind][0]
    while p_ > 0:
        if keep(c(p_)):
            count += 1
        if inc_child:
            count += count_child(p_, h_, contour)
        p_ = h_[p_][0]

    
    n = h_[ind][1]
    while n > 0:
        if keep(c(n)):
            count += 1
        if inc_child:
            count += count_child(n, h_, contour)
        n = h_[n][1]
    return count



def keep(contour):
    return keep_box(contour) and connected(contour)



def keep_box(contour):
    xx, yy, w_, h_ = cv2.boundingRect(contour)

    
    w_ *= 1.0
    h_ *= 1.0

     
    if w_ / h_ < 0.1 or w_ / h_ > 10:
        if DEBUG:
            print "\t Rejected because of shape: (" + str(xx) + "," + str(yy) + "," + str(w_) + "," + str(h_) + ")" + \
                  str(w_ / h_)
        return False
    
     
    if ((w_ * h_) > ((img_x * img_y) / 5)) or ((w_ * h_) < 15):
        if DEBUG:
            print "\t Rejected because of size"
        return False

    return True


def include_box(ind, h_, contour):
    if DEBUG:
        print str(ind) + ":"
        if is_child(ind, h_):
            print "\tIs a child"
            print "\tparent " + str(get_parent(ind, h_)) + " has " + str(
                count_child(get_parent(ind, h_), h_, contour)) + " child"
            print "\thas " + str(count_child(ind, h_, contour)) + " child"

    if is_child(ind, h_) and count_child(get_parent(ind, h_), h_, contour) <= 2:
        if DEBUG:
            print "\t skip"
        return False

    if count_child(ind, h_, contour) > 2:
        if DEBUG:
            print "\t skip"
        return False

    if DEBUG:
        print "\t keeping"
    return True

# Preprocessing
orig_img = cv2.imread(input_file)
img = cv2.copyMakeBorder(orig_img, 50, 50, 50, 50, cv2.BORDER_CONSTANT)

img_y = len(img)               #width
img_x = len(img[0])            #height

if DEBUG:
    print "Image is " + str(len(img)) + "x" + str(len(img[0]))

blue, green, red = cv2.split(img)

# Canny edge detection
blue_edges = cv2.Canny(blue, 200, 250)
green_edges = cv2.Canny(green, 200, 250)
red_edges = cv2.Canny(red, 200, 250)

edges = blue_edges | green_edges | red_edges

# contour detection
i,contours, hierarchy = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

hierarchy = hierarchy[0]

if DEBUG:
    processed = edges.copy()
    rejected = edges.copy()

keepers = []


for ind_, contour_ in enumerate(contours):
    if DEBUG:
        print "Processing #%d" % ind_

    x, y, w, h = cv2.boundingRect(contour_)

    if keep(contour_) and include_box(ind_, hierarchy, contour_):
       
        keepers.append([contour_, [x, y, w, h]])
        if DEBUG:
            cv2.rectangle(processed, (x, y), (x + w, y + h), (100, 100, 100), 1)
            cv2.putText(processed, str(ind_), (x, y - 5), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))
    else:
        if DEBUG:
            cv2.rectangle(rejected, (x, y), (x + w, y + h), (100, 100, 100), 1)
            cv2.putText(rejected, str(ind_), (x, y - 5), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255))

# Conversion of image into black and white image
new_image = edges.copy()
new_image.fill(255)
boxes = []

# Intensity calculation
for ind_, (contour_, box) in enumerate(keepers):

    fg_int = 0.0
    for p in contour_:
        fg_int += ii(p[0][0], p[0][1])

    fg_int /= len(contour_)
    if DEBUG:
        print "foreground intensity for #%d = %d" % (ind_, fg_int)

    
    x_, y_, width, height = box
    bg_int = \
        [
           
            ii(x_ - 1, y_ - 1),
            ii(x_ - 1, y_),
            ii(x_, y_ - 1),

            
            ii(x_ + width + 1, y_ - 1),
            ii(x_ + width, y_ - 1),
            ii(x_ + width + 1, y_),

           
            ii(x_ - 1, y_ + height + 1),
            ii(x_ - 1, y_ + height),
            ii(x_, y_ + height + 1),

            
            ii(x_ + width + 1, y_ + height + 1),
            ii(x_ + width, y_ + height + 1),
            ii(x_ + width + 1, y_ + height)
        ]

    
    bg_int = np.median(bg_int)    # Median of the pixels

   
    if fg_int >= bg_int:
        fg = 255
        bg = 0
    else:
        fg = 0
        bg = 255

        
    for x in range(x_, x_ + width):
        for y in range(y_, y_ + height):
            if y >= img_y or x >= img_x:
                if DEBUG:
                    print "pixel exceeding the bounds (%d,%d)" % (y, x)
                contourinue
            if ii(x, y) > fg_int:
                new_image[y][x] = bg
            else:
                new_image[y][x] = fg

# Improve OCR accuracy
new_image = cv2.blur(new_image, (2, 2))
cv2.imwrite(output_file, new_image)
if DEBUG:
    cv2.imwrite('edges.png', edges)
    cv2.imwrite('processed.png', processed)
    cv2.imwrite('rejected.png', rejected)
