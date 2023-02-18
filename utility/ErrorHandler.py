import logging


class ErrorHandler:
    def __init__(self, error, rtn):
        self.e = error
        self.rtn = rtn

    def return_error(self):
        self.rtn.msg = str(self.e)
        return self.rtn
