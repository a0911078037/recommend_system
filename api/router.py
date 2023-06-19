from __future__ import absolute_import

from .v1.first_test import FirstTest
from .v1.user import User
from .v1.login import Login
from .v1.question import Question
from .v1.question_type import QuestionType
from .v1.difficulty_type import DifficultyType
from .v1.submit_test import SubmitTest
from .v1.teacher import Teacher
from .v1.logout import Logout
from .v1.refresh_token import RefreshToken
from .v1.content_based_test import ContentBasedTest
from .v1.student import Student
from .v1.tf_idf import TF_IDF
from .v1.submit_survey import SubmitSurvey


router = [
    dict(resource=FirstTest, urls=['/first_test'], endpoint='first_test'),
    dict(resource=User, urls=['/user'], endpoint='user'),
    dict(resource=Login, urls=['/login'], endpoint='login'),
    dict(resource=Question, urls=['/question'], endpoint='question'),
    dict(resource=QuestionType, urls=['/question_type'], endpoint='question_type'),
    dict(resource=SubmitTest, urls=['/submit_test'], endpoint='submit_test'),
    dict(resource=Teacher, urls=['/teacher'], endpoint='teacher'),
    dict(resource=Logout, urls=['/logout'], endpoint='logout'),
    dict(resource=RefreshToken, urls=['/refresh_token'], endpoint='refresh_token'),
    dict(resource=ContentBasedTest, urls=['/content_based_test'], endpoint='content_based_test'),
    dict(resource=Student, urls=['/student'], endpoint='student'),
    dict(resource=TF_IDF, urls=['/tf_idf'], endpoint='tf_idf'),
    dict(resource=SubmitSurvey, urls=['/submit_survey'], endpoint='submit_survey'),
    dict(resource=DifficultyType, urls=['/difficulty_type'], endpoint='difficulty_type')
]

