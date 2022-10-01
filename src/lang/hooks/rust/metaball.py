import rust.metaball as metaball

def blob(seed: int, size: tuple[int, int], num_balls: tuple[int, int], inner_range: tuple[int, int], ball_size: tuple[int, int]):
    """Creates natural looking blob shapes using metaballs. Implemented in rust.

    Args:
        seed (int): The game seed to use
        size (tuple[int, int]): The maximum width and height of the generated blob
        num_balls (tuple[int, int]): The range of the number of metablobs to be used
        inner_range (tuple[int, int]): Maximum area in the area defined by "size" in which metaballs can be placed
        ball_size (tuple[int, int]): The range of different sizes a metaball can have

    Returns:
        dict: A dictionary of positions of the blob
    """
    return metaball.blob(seed, size, num_balls, inner_range, ball_size)
