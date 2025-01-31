import logging
from abc import ABC, abstractmethod

class CueListener(ABC):
    """An abstract class for objects that listen to the signals emitted from
    cueelists as they execute cues
    """


    def __init__(self):
        super().__init__()

    @abstractmethod
    def cueSignal(self, cuenum, master):
        pass