import cv2
import sun_functions

base_dir = '/home/pi/Desktop/Github/RPI_Eclipse/Scripts/Pictures'
file_name = '/frame_93_cam_2.jpg'
full_dir = base_dir + file_name

img = cv2.imread(full_dir)
r_sun = 150

img_bw = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
size_y, size_x, chan = img.shape
thresh = cv2.inRange(img_bw, (200), (255))
cv2.imwrite(base_dir + '/sun_th.jpg', thresh)

contours = sun_functions.contour_function(thresh)
if len(contours) == 0:
    raise ValueError(' ==> Error: There is no sun in picture.')
stat, center_x, center_y, radius = sun_functions.is_sun(contours, r_sun)
print '-> Sun radius: ', radius
if stat == 4:
    raise ValueError(' ==> Error: Can not find the sun!')
cut_factor = 1.3
cut_radius = int(cut_factor * radius)
test_edge = sun_functions.test_edge_sun(size_x, size_y, center_x, center_y, cut_radius) 
if test_edge == 1:
    raise ValueError(' ==> Error: The sun is in the edge of the picture.')
crop_img_sun = img_bw[center_y - cut_radius:center_y + cut_radius, center_x - cut_radius:center_x + cut_radius]

cv2.imwrite(base_dir + '/sun.jpg', crop_img_sun)
