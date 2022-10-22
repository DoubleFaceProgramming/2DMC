import numpy as np
import pygame
import cv2

kernel_top = cv2.getGaussianKernel(64 * 2, 70).reshape([1, -1]) # Create gaussian kernel
kernel_top /= kernel_top.max() # Normalize the kernel
kernel_top = kernel_top[: 64, : 64] # Cut out the top half
kernel_top = np.expand_dims(kernel_top, axis=2) # Reshape to [h, w, 1]
kernel_right = np.rot90(kernel_top)
kernel_bottom = np.rot90(kernel_right)
kernel_left = np.rot90(kernel_bottom)

vignette_lookup = {
    (0, -1): kernel_top,
    (-1, 0): kernel_left,
    (0, 1): kernel_bottom,
    (1, 0): kernel_right,
}

def overlap_vignette(kernels) -> np.ndarray:
    result = np.full((64, 64, 1), 1, "float64")
    for kernel in kernels:
        result *= kernel * 1.025
    return result

def apply_vignette(img: pygame.Surface, kernel: np.ndarray, darken: float = 1) -> pygame.Surface:
    img_array = pygame.surfarray.array3d(img)
    result_array = np.multiply(img_array, kernel * darken) # Applies the kernel modifications onto the image with matrix multiplication
    result = pygame.surfarray.make_surface(result_array.astype("uint8"))
    return result