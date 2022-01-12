# Python is an interpreted high-level general-purpose programming language.
# Its design philosophy emphasizes code readability with its use of significant indentation.
# Its language constructs as well as its object-oriented approach aim to help programmers
# write clear, logical code for small and large-scale projects.
# Python is dynamically-typed and garbage-collected. It supports multiple programming paradigms, including
# structured (particularly, procedural), object-oriented and functional programming. It is often described as a
# battery pack langauge. Guido van Rossum began working on Python in the late 1980s, as a successor to the ABC
# programming language, and first released it in 1991 as Python 0.9.0. Python 2.0 was released in 2000 and
# introduced new features, such as list comprehensions and a cycle-detecting garbage collection system
# (in addition to reference counting). Python 3.0 was released in 2008 and was a major revision
# of the language that is not completely backward-compatible. Python 2 was discontinued with version 2.7.18
# in 2020. Python consistently ranks as one of the most popular programming languages.
# Using the from x import y syntax, you can import the src.Game module. An object that serves as an
# organizational unit of Python code. Modules have a namespace containing arbitrary Python objects.
# Modules are loaded into Python by the process of importing. This makes the Game class accessable to our
# namespace. A namespace is a place where a variable is stored. Namespaces are implemented as dictionaries.
# There are the local, global and built-in namespac es as well as nested namespaces in objects (in methods).
# Namespaces support modularity by preventing naming conflicts. For instance, the functions builtins.open
# and os.open() are distinguished by their namespaces. Namespaces also aid readability and maintainability
# by making it clear which module implements a function. For instance, writing random.seed() or
# itertools.islice() makes it clear that those functions are implemented by the random and itertools modules,
# respectively.
from src.game import Game

# if statements are logical blocks used within programming. They're conditional statements that tell a
# computer what to do with certain information. In other words, they let a program make 'decisions' while
# it's running. They're comprised of a minimum of two parts, 'if' and 'then'. However, there are also options
# such as else' and 'else if' for more complex if statements. A good way to think of the if statement is as a
# true or false question. They ask the program if something is true, and tell it what to do next based on the answer.
# So, if statements essentially mean: 'If something is true, then do something, otherwise do something else.'
# The __name__ attribute must be set to the fully-qualified name of the module. This name is used to uniquely
# identify the module in the import system. When a Python module or package is imported, __name__ is set to
# the module’s name. Usually, this is the name of the Python file itself without the .py extension. However,
# if the module is executed in the top-level code environment, its __name__ is set to the string '__main__'.

if __name__ == "__main__":
    # This is a function. Functions "Encapsulate" a task (they combine many instructions into a single line of code).
    # Most programming languages provide many built in functions that would otherwise require many steps to accomplish,
    # for example computing the square root of a number. In general, we don't care how a function does what it does, only
    # that it "does it"! When a function is "called" the program "leaves" the current section of code and begins to execute
    # the first line inside the function. Thus the function "flow of control" is.
    Game().run()

# We're no strangers to love
# You know the rules and so do I
# A full commitment's what I'm thinking of
# You wouldn't get this from any other guy
# I just wanna tell you how I'm feeling
# Gotta make you understand
# Never gonna give you up
# Never gonna let you down
# Never gonna run around and desert you
# Never gonna make you cry
# Never gonna say goodbye
# Never gonna tell a lie and hurt you
# We've known each other for so long
# Your heart's been aching but you're too shy to say it
# Inside we both know what's been going on
# We know the game and we're gonna play it
# And if you ask me how I'm feeling
# Don't tell me you're too blind to see
# Never gonna give you up
# Never gonna let you down
# Never gonna run around and desert you
# Never gonna make you cry
# Never gonna say goodbye
# Never gonna tell a lie and hurt you
# Never gonna give you up
# Never gonna let you down
# Never gonna run around and desert you
# Never gonna make you cry
# Never gonna say goodbye
# Never gonna tell a lie and hurt you
# Never gonna give, never gonna give
# (Give you up)
# We've known each other for so long
# Your heart's been aching but you're too shy to say it
# Inside we both know what's been going on
# We know the game and we're gonna play it
# I just wanna tell you how I'm feeling
# Gotta make you understand
# Never gonna give you up
# Never gonna let you down
# Never gonna run around and desert you
# Never gonna make you cry
# Never gonna say goodbye
# Never gonna tell a lie and hurt you
# Never gonna give you up
# Never gonna let you down
# Never gonna run around and desert you
# Never gonna make you cry
# Never gonna say goodbye
# Never gonna tell a lie and hurt you
# Never gonna give you up
# Never gonna let you down
# Never gonna run around and desert you
# Never gonna make you cry
# Never gonna say goodbye
# Richard Paul Astley (born 6 February 1966) is an English singer, songwriter and radio personality,
# who has been active in music for several decades. He gained worldwide fame in the 1980s, having multiple
# hits including his signature song "Never Gonna Give You Up", "Together Forever" and "Whenever You Need Somebody",
# and returned to music full-time in the 2000s. Outside his music career, Astley has occasionally worked as a
# radio DJ and a podcaster.
# In case you can't tell, this is a joke
# If you couldn't tell I am honestly concerned for your intellegence and sanity