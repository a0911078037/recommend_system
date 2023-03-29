from __future__ import absolute_import

from .v1.test import test
from .v1.user import User
from .v1.login import Login
from .v1.question import Question
from .v1.question_type import QuestionType
from .v1.difficulty_type import DifficultyType

router = [
    dict(resource=test, urls=['/test'], endpoint='test'),
    dict(resource=User, urls=['/user'], endpoint='user'),
    dict(resource=Login, urls=['/login'], endpoint='login'),
    dict(resource=Question, urls=['/question'], endpoint='question'),
    dict(resource=QuestionType, urls=['/question_type'], endpoint='question_type'),
    dict(resource=DifficultyType, urls=['/difficulty_type'], endpoint='difficulty_type')
]

