from __future__ import absolute_import
from .v1.test import test

router = [
    dict(resource=test, urls=['/test'], endpoint='test')
    ]

