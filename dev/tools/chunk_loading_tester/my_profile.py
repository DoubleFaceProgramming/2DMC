from pstats import SortKey, Stats
from typing import Callable, Any
from datetime import datetime
from cProfile import Profile
from pathlib import Path
from os.path import join
import subprocess

def profile_chunk(callable: Callable[..., Any], *args: tuple[Any]) -> Any:
    """Profiles the given callable and saves + prints the results
    Args:
        callable (type): A callabale type (function, constructor, ect)
    Returns:
        [...]: The result of calling the callable
    """

    with Profile() as profile: # Profiling the contents of the with block
        returnval = callable(*args)     # Calling the callable with the args

    # Naming the profile file in the format "chunk-{x},{y}-{hour}-{minute}-{second}.prof"
    statfile = Path(join("profiles", f"chunk-{int(args[0][0])},{int(args[0][1])}-{datetime.now().strftime('%H-%M-%S')}.prof"))

    stats = Stats(profile).sort_stats(SortKey.TIME) # Sorting the stats from highest time to lowest
    stats.dump_stats(filename=str(statfile)) # Saving the stats to a profile file
    print(f"\n\n Profile saved to: {str(statfile)}!\n\n")
    subprocess.Popen(["snakeviz", str(statfile)])
    return returnval

def profile(callable: Callable[..., Any], *args: tuple[Any]) -> Any:
    """Profiles the given callable and saves + prints the results
    Args:
        callable (type): A callabale type (function, constructor, ect)
    Returns:
        [...]: The result of calling the callable
    """

    with Profile() as profile: # Profiling the contents of the with block
        returnval = callable(*args)     # Calling the callable with the args

    statfile = Path(join("profiles", f"profile-{datetime.now().strftime('%H-%M-%S')}.prof"))

    stats = Stats(profile).sort_stats(SortKey.TIME) # Sorting the stats from highest time to lowest
    stats.dump_stats(filename=str(statfile)) # Saving the stats to a profile file
    print(f"\n\n Profile saved to: {str(statfile)}!\n\n")
    subprocess.Popen(["snakeviz", str(statfile)])
    return returnval