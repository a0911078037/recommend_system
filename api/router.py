from __future__ import absolute_import

from .v1.test import test
from .v1.user import User
from .v1.login import Login
from .v1.question import Question

router = [
    dict(resource=test, urls=['/test'], endpoint='test'),
    dict(resource=User, urls=['/user'], endpoint='user'),
    dict(resource=Login, urls=['/login'], endpoint='login'),
    dict(resource=Question, urls=['/question'], endpoint='question')
]

