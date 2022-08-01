from pathlib import Path
from io import BufferedReader

# Replacement for open("file","rb") with a callback
# on each read, for tracking progress in some 3rd party
# libraries that don't support it normally but take a
# file-like object (I'm looking at you aiohttp)
class ProgressFileReader(BufferedReader):
    def __init__(self, filename, read_callback):
        f = open(filename, "rb")
        self.__read_callback = read_callback
        super().__init__(raw=f)
        self.length = Path(filename).stat().st_size

    def read(self, size=None):
        calc_sz = size
        if not calc_sz:
            calc_sz = self.length - self.tell()
        self.__read_callback(self.tell(), self.length)
        return super(ProgressFileReader, self).read(size)
