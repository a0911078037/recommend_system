from __future__ import absolute_import

from .v1.test import test
from .v1.user import User

router = [
    dict(resource=test, urls=['/test'], endpoint='test'),
    dict(resource=User, urls=['/user'], endpoint='user')
]

