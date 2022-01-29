import sys

class ArgParser:
    """A class that handles the parsing of CL arguments.
    Not that a lot of this is probably temporary and will be reworked"""

    def __init__(self) -> None:
        self.args = sys.argv[1:]
        self.parsed = {}

        # Creating a dictionary to contain the CLA
        # Basically we cloop through the CLA, remove the '--',
        # and set the value to None if there is no arguemnt, or to
        # the argument if there is one.
        # Check stops us from looping over something twice
        # (ex. python main.py --profile test, check means we only loop
        # over --profile and not test)
        check = False
        for arg in self.args:
            if not check:
                # [2:] to get rid of the '--'
                self.parsed[arg[2:]] = check = self.get_val(arg)

    def get_val(self, option: str) -> str | None:
        """Returns the value of the option passed as a CLA

        Arguments:
            option (str): The argument to check (ex. "--profile")

        Returns:
            [str or None]: A str that contains the value of the option or None if the option does not exist
        """

        val = None
        try:
            # Getting the item at the index one in fornt of the option.
            val = self.args[self.args.index(option) + 1]
        except (ValueError, IndexError):
            pass

        return val