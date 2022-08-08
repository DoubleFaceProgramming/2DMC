from multipledispatch import dispatch

from src.utils.constants import VEC

# The clamp functions clamps a value to the max or min if it exceeds them

@dispatch((int, float), (int, float), (int, float))
def clamp(val: int | float, min_val: int | float, max_val: int | float):
    if val < min_val:
        return min_val, -1 # Also returns whether the value was clamped to the min value (-1)
    elif val > max_val:
        return max_val, 1 # or if it was clamped to the max value (1)
    return val, 0 # or if it wasn't clamped (0)

# Clamp to vector values
@dispatch(VEC, VEC, VEC)
def clamp(val: VEC, min_val: VEC, max_val: VEC):
    val = val.copy()
    direction = VEC(0, 0)
    if val.x < min_val.x:
        val.x = min_val.x
        direction.x = -1 # Clamped x to min value
    elif val.x > max_val.x:
        val.x = max_val.x
        direction.x = 1 # Clamped x to max value
    if val.y < min_val.y:
        val.y = min_val.y
        direction.y = -1 # Clamped y to min value
    elif val.y > max_val.y:
        val.y = max_val.y
        direction.y = 1 # Clamped y to max value
    return val.copy(), direction.copy()

# Clamp to only a max value
@dispatch((int, float), (int, float))
def clamp_max(val: int | float, max_val: int | float):
    if val > max_val:
        return max_val, 1
    return val, 0

# Clamp to only a max vector value
@dispatch(VEC, VEC)
def clamp_max(val: VEC, max_val: VEC):
    val = val.copy()
    direction = VEC(0, 0)
    if val.x > max_val.x:
        val.x = max_val.x
        direction.x = 1
    if val.y > max_val.y:
        val.y = max_val.y
        direction.y = 1
    return val.copy(), direction.copy()

# Clamp to only a min value
@dispatch((int, float), (int, float))
def clamp_min(val: int | float, min_val: int | float):
    if val < min_val:
        return min_val, -1
    return val, 0

# Clamp to only a min vector value
@dispatch(VEC, VEC)
def clamp_min(val: VEC, min_val: VEC):
    val = val.copy()
    direction = VEC(0, 0)
    if val.x < min_val.x:
        val.x = min_val.x
        direction.x = -1
    if val.y < min_val.y:
        val.y = min_val.y
        direction.y = -1
    return val.copy(), direction.copy()

# The snap function snaps a value to a central value if it enters a certain offset around the central value
def snap(val: int | float, snap_val: int | float, offset: int | float):
    if snap_val - offset < val < snap_val + offset:
        return snap_val
    return val