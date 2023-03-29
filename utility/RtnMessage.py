class RtnMessage:
    def __init__(self, _msg='', _state=True, _result=None):
        self.msg = _msg
        self.state = _state
        self.result = [] if not _result else [_result]

    def to_dict(self):
        data = {
            'msg': self.msg,
            'state': self.state,
            'result': self.result
        }
        return data

