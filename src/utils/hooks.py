from fishhook import hook

@hook(list)
def reverse_nip(self):
    rev = self.copy()
    rev.reverse()
    return rev