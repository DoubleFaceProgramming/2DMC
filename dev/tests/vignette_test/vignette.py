import numpy as np
import pygame
import cv2

# Create a gaussian kernel on each axis
horizontal_kernel = cv2.getGaussianKernel(64 * 3, 50 * 2).reshape([1, -1]) # Essentially rotates it to be horizontal
vertical_kernel = cv2.getGaussianKernel(64 * 3, 50 * 2)
kernel_3x3 = horizontal_kernel * vertical_kernel # Merge the horizontal kernel and vertical kernel into a 2D kernel
kernel_3x3 /= kernel_3x3.max() # Normalize the kernel
kernel_3x3 = np.expand_dims(kernel_3x3, axis=2) # Reshape to [h, w, 1] so that multiplication can be applied
kernel_3x3_1 = kernel_3x3[:64, :64]
kernel_3x3_2 = kernel_3x3[64:64*2, :64]
kernel_3x3_3 = kernel_3x3[64*2:64*3, :64]
kernel_3x3_4 = kernel_3x3[:64, 64:64*2]
kernel_3x3_5 = kernel_3x3[64:64*2, 64:64*2]
kernel_3x3_6 = kernel_3x3[64*2:64*3, 64:64*2]
kernel_3x3_7 = kernel_3x3[:64, 64*2:64*3]
kernel_3x3_8 = kernel_3x3[64:64*2, 64*2:64*3]
kernel_3x3_9 = kernel_3x3[64*2:64*3, 64*2:64*3]

# Vertial 1x3
horizontal_kernel = cv2.getGaussianKernel(64, 50).reshape([1, -1])
vertical_kernel = cv2.getGaussianKernel(64 * 3, 50 * 3)
kernel_1x3 = horizontal_kernel * vertical_kernel
kernel_1x3 /= kernel_1x3.max()
kernel_1x3 = np.expand_dims(kernel_1x3, axis=2)

# Horizontal 3x1
horizontal_kernel = cv2.getGaussianKernel(64 * 3, 50 * 3).reshape([1, -1])
vertical_kernel = cv2.getGaussianKernel(64, 50)
kernel_3x1 = horizontal_kernel * vertical_kernel
kernel_3x1 /= kernel_3x1.max()
kernel_3x1 = np.expand_dims(kernel_3x1, axis=2)

horizontal_kernel = cv2.getGaussianKernel(64, 50).reshape([1, -1])
vertical_kernel = cv2.getGaussianKernel(64, 50)
kernel_1x1 = horizontal_kernel * vertical_kernel
kernel_1x1 /= kernel_1x1.max()
kernel_1x1 = np.expand_dims(kernel_1x1, axis=2)

# def get_vignette(neighbors: set) -> np.ndarray:
#     corners = []
#     if (-1, 0) in neighbors and (0, 1) in neighbors:
#         corners.append("bottomleft")
#     if (1, 0) in neighbors and (0, 1) in neighbors:
#         corners.append("bottomright")
#     if (-1, 0) in neighbors and (0, -1) in neighbors:
#         corners.append("topleft")
#     if (1, 0) in neighbors and (0, -1) in neighbors:
#         corners.append("topright")

def apply_vignette(img: pygame.Surface, kernel: np.ndarray) -> pygame.Surface:
    img_array = pygame.surfarray.array3d(img)
    result_array = np.multiply(img_array, kernel) # Applies the kernel modifications onto the image with matrix multiplication
    result = pygame.surfarray.make_surface(result_array.astype("uint8"))
    return result

# img = pygame.image.load("test.png")
# vignette = get_vignette(set())
# result = apply_vignette(img, vignette)