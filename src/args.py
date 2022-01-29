import sys

class ArgParser:
    """A class that handles the parsing of CL arguments.
    Not that a lot of this is probably temporary and will be reworked"""

    def __init__(self) -> None:
        self.args = sys.argv[1:]
        self.parsed = {}
        
        # self.parsed will contain all the CLAs as keys, and their arguements as values
        # Values will be None if there is no arguement
        # (ex. python main.py --profile test, profile will be the key and test will be the value)
        for arg in self.args:
            if arg.startswith("--"):
                # "--" is removed with [2:]
                self.parsed[arg[2:]] = self.get_val(arg)

    def get_val(self, option: str) -> str | None:
        """Returns the value of the option passed as a CLA

        Arguments:
            option (str): The argument to check (ex. "--profile")

        Returns:
            [str or None]: A str that contains the value of the option or None if the option does not exist
        """

        val = None
        try:
            # Getting the item at the index one in front of the option, if it does not start with "--"
            val = arg if not (arg := self.args[self.args.index(option) + 1]).startswith("--") else None
        except (ValueError, IndexError):
            pass

        return val