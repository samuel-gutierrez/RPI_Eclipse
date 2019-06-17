"""
A set of functions used to detect the sun in an image
"""
import cv2


def test_sat(thresh, sizex, sizey, len_sat=400):
    """
    Test if the image is over saturated
    -----------------------------
    Inputs : Thresholded image, image size, saturation lenght 
    Outputs: 1 if image is saturated
             0 if not
    """
    aux1 = min(sizex, sizey)
    counter = 0
    for ii in range(aux1):
        counter += thresh[ii][ii]/255
    if counter > len_sat:
        aux2 = 1
    else:
        aux2 = 0
    return aux2


def contour_function(thresh):
    """
    Find the contours of an image that is thresholded
    -----------------------------
    Input : np.ndarray (threshold)
    Output: np.ndarray (list of contours)
    """
    smooth_thresh = cv2.GaussianBlur(thresh, (3, 3), 0)
    (_, cnts, _) = cv2.findContours(smooth_thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return cnts


def test_edge_sun(size_x, size_y, center_x, center_y, cut_radius):
    """
    Test if the sun is in the edge of the frame
    -----------------------------
    Input : Size of the image, shape of the sun (int)
    Output: 0 if the sun is completely inside the picture
            1 if not
    """
    if center_y - cut_radius < 0 or center_y + cut_radius > size_y or center_x - cut_radius < 0 or center_x + cut_radius > size_x:
        value = 1
    else:
        value = 0
    return value


def is_sun(cnts, r_sun):
    """
    Test if any contour have a similar size to the sun
    -----------------------------
    Input : List of contours, estimated radius of the sun in the image
    Output: Status (= 0 if similar; = 1 if not), sun shape
    """
    stat = 1
    x_center = 0
    y_center = 0
    R = 0
    sorted_contours = sorted(cnts, key=cv2.contourArea, reverse=True)
    for contour in sorted_contours:
        pos, radius = cv2.minEnclosingCircle(contour)
        R = int(radius)
        if 5 <= R <= r_sun:
            x_center = int(pos[0])
            y_center = int(pos[1])
            stat = 0
            break
    return stat, x_center, y_center, R


def sun_detect(img, r_sun):
    """
    Developed algorithm to detect and cut the sun in the image
    -----------------------------
    Input : Image, estimated radius of the sun in the image
    Output: B&W cropped image of the sun (np.ndarray)
    """
    img_bw = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    size_y, size_x, chan = img.shape
    thresh = cv2.inRange(img_bw, (200), (255))
    contours = contour_function(thresh)
    if len(contours) == 0:
        raise ValueError(' ==> Error: There is no sun in picture.')
    stat, center_x, center_y, radius = is_sun(contours, r_sun)
    if stat == 1:
        raise ValueError(' ==> Error: Can not find the sun!')
    cut_factor = 1.3
    cut_radius = int(cut_factor * radius)
    test_edge = test_edge_sun(size_x, size_y, center_x, center_y, cut_radius) 
    if test_edge == 1:
        raise ValueError(' ==> Error: The sun is in the edge of the picture.')
    crop_img_sun = img_bw[center_y - cut_radius:center_y + cut_radius, center_x - cut_radius:center_x + cut_radius]
    return crop_img_sun
