from enum import Enum
import logging

class Utility(Enum):
    LGF = 1
    SGF = 2
    
# create a function that maps a string to a Utility enum
def str_to_utility(s):
    if s == "LGF":
        return Utility.LGF
    elif s == "SGF":
        return Utility.SGF
    else:
        raise ValueError("Invalid utility string")
       
class DebugLevel(Enum):
    TRACE = 5
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    
class SchedulingAlgorithm(Enum):
    FIFO = 1
    SDF = 2 # shortest duration first
    
class Environment(Enum):
    BARE_METAL = 1
    KUBERNETES = 2
