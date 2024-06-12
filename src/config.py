from enum import Enum
import logging

class Utility(Enum):
    LGF = 1
       
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
