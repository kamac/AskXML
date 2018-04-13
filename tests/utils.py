import tempfile
import os

class TempFile:
    """ Makes a tempfile but allows IO on it without blocking. Can be used with the 'with' keyword """

    def __init__(self, *args, **kwargs):
        handle, self.__file_path = tempfile.mkstemp(*args, **kwargs)
        os.close(handle)

    def write(self, *args, **kwargs):
        with open(self.__file_path, mode='w') as f:
            f.write(*args, **kwargs)

    @property
    def name(self):
        return self.__file_path

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        os.remove(self.__file_path)