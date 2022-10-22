import numpy as np
import pygame
import cv2

left = (-1, 0)
right = (1, 0)
top = (0, -1)
bottom = (0, 1)

# Create a gaussian kernel on each axis
vertical_kernel = cv2.getGaussianKernel(64 * 3, 110).reshape([1, -1]) # Essentially rotates it to be vertical
horizontal_kernel = cv2.getGaussianKernel(64 * 3, 110)
kernel_3x3 = vertical_kernel * horizontal_kernel # Merge the horizontal kernel and vertical kernel into a 2D kernel
kernel_3x3 /= kernel_3x3.max() # Normalize the kernel
kernel_3x3 = np.expand_dims(kernel_3x3, axis=2) # Reshape to [h, w, 1] so that multiplication can be applied

# Horizontal 3x1
vertical_kernel = cv2.getGaussianKernel(64, 50).reshape([1, -1])
horizontal_kernel = cv2.getGaussianKernel(64 * 3, 90)
kernel_3x1 = vertical_kernel * horizontal_kernel
kernel_3x1 /= kernel_3x1.max()
kernel_3x1 = np.expand_dims(kernel_3x1, axis=2)

# Vertical 1x3
vertical_kernel = cv2.getGaussianKernel(64 * 3, 90).reshape([1, -1])
horizontal_kernel = cv2.getGaussianKernel(64, 50)
kernel_1x3 = vertical_kernel * horizontal_kernel
kernel_1x3 /= kernel_1x3.max()
kernel_1x3 = np.expand_dims(kernel_1x3, axis=2)

# Vertical 2x2
vertical_kernel = cv2.getGaussianKernel(64 * 2, 150).reshape([1, -1])
horizontal_kernel = cv2.getGaussianKernel(64 * 2, 60)
kernel_2x3 = vertical_kernel * horizontal_kernel
kernel_2x3 /= kernel_2x3.max()
kernel_2x3 = np.expand_dims(kernel_2x3, axis=2)

# 1x1
vertical_kernel = cv2.getGaussianKernel(64, 40).reshape([1, -1])
horizontal_kernel = cv2.getGaussianKernel(64, 40)
kernel_1x1 = vertical_kernel * horizontal_kernel
kernel_1x1 /= kernel_1x1.max()
kernel_1x1 = np.expand_dims(kernel_1x1, axis=2)

kernel_3x3_topleft = kernel_3x3[: 64, : 64]
kernel_3x3_top = kernel_3x3[64 : 64 * 2, : 64]
kernel_3x3_topright = kernel_3x3[64 * 2 : 64 * 3, : 64]
kernel_3x3_left = kernel_3x3[: 64, 64 : 64 * 2]
kernel_3x3_middle = kernel_3x3[64 : 64 * 2, 64 : 64 * 2]
kernel_3x3_right = kernel_3x3[64 * 2 : 64 * 3, 64 : 64 * 2]
kernel_3x3_bottomleft = kernel_3x3[: 64, 64 * 2 : 64 * 3]
kernel_3x3_bottom = kernel_3x3[64 : 64 * 2, 64 * 2 : 64 * 3]
kernel_3x3_bottomright = kernel_3x3[64 * 2 : 64 * 3, 64 * 2 : 64 * 3]

kernel_1x3_top = kernel_1x3[: 64, : 64]
kernel_1x3_middle = kernel_1x3[64 : 64 * 2, : 64]
kernel_1x3_bottom = kernel_1x3[64 * 2 : 64 * 3, : 64]

kernel_3x1_left = kernel_3x1[: 64, : 64]
kernel_3x1_middle = kernel_3x1[: 64, 64 : 64 * 2]
kernel_3x1_right = kernel_3x1[: 64, 64 * 2 : 64 * 3]

kernel_2x3_top = kernel_2x3[32 : 64 + 32, : 64] # Only way I can think of to do this, very scuffed

vignette_lookup = {
    (top, left): kernel_3x3_topleft,
    (left, bottom): kernel_3x3_bottomleft,
    (right, bottom): kernel_3x3_bottomright,
    (top, right): kernel_3x3_topright,
    (top, ): kernel_3x3_top,
    (left, ): kernel_3x3_left,
    (bottom, ): kernel_3x3_bottom,
    (right, ): kernel_3x3_right,
    (): kernel_3x3_middle,
    (left, right): kernel_1x3_middle,
    (top, bottom): kernel_3x1_middle,
    (top, left, bottom): kernel_3x1_left,
    (left, right, bottom): kernel_1x3_bottom,
    (top, right, bottom): kernel_3x1_right,
    (top, left, right): kernel_1x3_top,
    (top, left, right, bottom): kernel_1x1
}

def apply_vignette(img: pygame.Surface, kernel: np.ndarray, darken: float = 1) -> pygame.Surface:
    img_array = pygame.surfarray.array3d(img)
    result_array = np.multiply(img_array, kernel * darken) # Applies the kernel modifications onto the image with matrix multiplication
    result = pygame.surfarray.make_surface(result_array.astype("uint8"))
    return result