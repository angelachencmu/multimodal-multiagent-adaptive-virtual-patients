from .ltm import LTM
from .summary import Summary
from .SEM import SEM

class MemoryRoom:
    def __init__(self):
        self.ltm = LTM()
        self.summary = Summary()
        self.sem = SEM()
        self.history = []
