import numpy as np
import cv2

img = cv2.imread("test2.png") / 255 # Read image, "/ 255" normalizes the colors of the image
height, width = img.shape[:2]

kernel_top = cv2.getGaussianKernel(height * 2, 200) # Create gaussian kernel
kernel_top /= kernel_top.max() # Normalize the kernel
kernel_top = kernel_top[: height, : width] # Cut out the top half
kernel_top = np.expand_dims(kernel_top, axis=2) # Reshape to [h, w, 1]
kernel_left = np.rot90(kernel_top)
kernel_bottom = np.rot90(kernel_left)
kernel_right = np.rot90(kernel_bottom)

# cv2.imshow("Vignette 1", result)

# cv2.waitKey()