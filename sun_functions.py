"""
A set of functions used to detect the sun in an image
"""
import cv2
import numpy as np


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


def find_local_max(array, local_max_tol=50):
    """
    Find all the local maximum in the histogram array
    -----------------------------
    """
    dev1 = np.gradient(array)
    dev2 = np.gradient(dev1)
    list_local_max = []
    list_index_local_max = []
    for ii in range(len(array)):
        if dev1[ii] > local_max_tol and dev2[ii] < 0:
            list_local_max.append(array[ii+1])
            list_index_local_max.append(ii+1)
    return list_local_max, list_index_local_max


def intensity(img_bw):
    """
    Find the intensity of the last (sun) local max in the histogram of the picture
    -----------------------------
    Input: bw image (np.ndararry)
    Return: local_max (int [0, 256])
    """
    hist = cv2.calcHist([img_bw], [0], None, [256], [0,256])
    hist_array = np.concatenate(hist)
    hist_array = np.append(hist_array, 0)
    local_max_values, local_max_index = find_local_max(hist_array)
    index = local_max_index[-1]
    good_index = index - 5
    if good_index < 0:
        good_index = 0
    return good_index


def is_circle(contour, circle_tolerance_factor=0.2, count_factor_tolerance=0.2):
    """
    Verify if a contour has a circle shape
    -----------------------------
    Input: contour (np.ndarray), circle_tolerance_factor (float), count_tolerance_factor (float)
    Return: stat ---> 0 if is circle,
                      1 if doesnt
    """
    pos, radius = cv2.minEnclosingCircle(contour)
    R = int(radius)
    x_center = int(pos[0])
    y_center = int(pos[1])
    count = 0
    stat = 0
    perimeter = len(contour)
    count_tolerance = count_factor_tolerance * perimeter
    for point in contour:
        diff = ((point[0][0] - x_center)**2 +  (point[0][1] - y_center)**2)**(0.5)
        if abs(diff - R) > circle_tolerance_factor*R:
            count += 1
        if count > count_tolerance:
            stat = 1
    return stat, x_center, y_center, R


def is_sun(cnts, r_sun):
    """
    Checks whether a contour have size and shape similar to the sun
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
        iscircle, x_center, y_center, R = is_circle(contour)
        if iscircle == 0 and (5 <= R <= r_sun):
            stat = 0
            break
    return stat, x_center, y_center, R


def sun_detect(img, r_sun, cut_sun_factor=1.4):
    """
    Developed algorithm to detect and cut the sun in the RPI image
    -----------------------------
    Input : Image, estimated radius of the sun in the image
    Output: B&W cropped image of the sun (np.ndarray)
    """
    img_bw = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    size_y, size_x, chan = img.shape
    intensity_value = intensity(img_bw)
    if intensity_value == 0:
        raise ValueError(' ==> Error: Can not find a good intensity threshold value in the image.')
    thresh = cv2.inRange(img_bw, intensity_value, 255)
    contours = contour_function(thresh)
    if len(contours) == 0:
        raise ValueError(' ==> Error: Can not find any contours in the thresholded image.')
    stat, center_x, center_y, radius = is_sun(contours, r_sun)
    if stat == 1:
        raise ValueError(' ==> Error: The algorithm can not find the sun shape in the image.')
    cut_radius = int(cut_sun_factor * radius)
    test_edge = test_edge_sun(size_x, size_y, center_x, center_y, cut_radius) 
    if test_edge == 1:
        raise ValueError(' ==> Error: The sun is in the edge of the picture.')
    crop_img_sun = img_bw[center_y - cut_radius:center_y + cut_radius, center_x - cut_radius:center_x + cut_radius]
    return crop_img_sun
