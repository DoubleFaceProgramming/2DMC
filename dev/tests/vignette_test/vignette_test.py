from cv2 import getGaussianKernel, imshow, waitKey, imread
import numpy as np

img = imread("test2.png") / 255 # Read image, "/ 255" normalizes the colors of the image
height, width = img.shape[:2]

# Create a gaussian kernel on each axis
kernel_x = getGaussianKernel(width * 2, 80 * 2).reshape([1, -1]) # Essentially rotates it to be horizontal
kernel_y = getGaussianKernel(height * 2, 80 * 2)

kernel = kernel_x * kernel_y # Merge the horizontal kernel and vertical kernel
kernel /= kernel.max() # Normalize the kernel
kernel = kernel[height:, width:]

kernel = np.expand_dims(kernel, axis=2) # Reshape to [h, w, 1] so that multiplication can be applied
result = np.multiply(img, kernel) # Applies the kernel modifications onto the image with matrix multiplication

imshow("Offset Vignette 1", result)

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

# Create a gaussian kernel on each axis
kernel_x = getGaussianKernel(width * 2, 80 * 2).reshape([1, -1]) # Essentially rotates it to be horizontal
kernel_y = getGaussianKernel(height, 80)

kernel = kernel_x * kernel_y # Merge the horizontal kernel and vertical kernel
kernel /= kernel.max() # Normalize the kernel
kernel = kernel[:, width:]

kernel = np.expand_dims(kernel, axis=2) # Reshape to [h, w, 1] so that multiplication can be applied
result = np.multiply(img, kernel) # Applies the kernel modifications onto the image with matrix multiplication

imshow("Offset Vignette 2", result)

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

# Create a gaussian kernel on each axis
kernel_x = getGaussianKernel(width * 2, 80 * 2).reshape([1, -1]) # Essentially rotates it to be horizontal
kernel_y = getGaussianKernel(height * 3, 80 * 3)

kernel = kernel_x * kernel_y # Merge the horizontal kernel and vertical kernel
kernel /= kernel.max() # Normalize the kernel
kernel = kernel[height:height * 2, width:]

kernel = np.expand_dims(kernel, axis=2) # Reshape to [h, w, 1] so that multiplication can be applied
result = np.multiply(img, kernel) # Applies the kernel modifications onto the image with matrix multiplication

imshow("Offset Vignette 3", result)

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

# Create a gaussian kernel on each axis
kernel_x = getGaussianKernel(width * 2, 80 * 2).reshape([1, -1]) # Essentially rotates it to be horizontal
kernel_y = getGaussianKernel(height * 3, 80 * 3)

kernel = kernel_x * kernel_y # Merge the horizontal kernel and vertical kernel
kernel /= kernel.max() # Normalize the kernel
kernel = kernel[height:height * 2, width:]

kernel = np.expand_dims(kernel, axis=2) # Reshape to [h, w, 1] so that multiplication can be applied
result = np.multiply(img, kernel) # Applies the kernel modifications onto the image with matrix multiplication

imshow("Offset Vignette 4", result)

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

# Create a gaussian kernel on each axis
kernel_x = getGaussianKernel(width, 80).reshape([1, -1]) # Essentially rotates it to be horizontal
kernel_y = getGaussianKernel(height, 80)

kernel = kernel_x * kernel_y # Merge the horizontal kernel and vertical kernel
kernel /= kernel.max() # Normalize the kernel

kernel = np.expand_dims(kernel, axis=2) # Reshape to [h, w, 1] so that multiplication can be applied
result = np.multiply(img, kernel) # Applies the kernel modifications onto the image with matrix multiplication

imshow("Vignette", result)

waitKey()