from flask_restx import Resource
from flask import request
from utility.RtnMessage import RtnMessage
from app import config
from data_access.query.question_query import QuestionQuery
import uuid
from utility.logger import get_logger
import os
import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity


class Question(Resource):
    logger = get_logger('Question')
    image_type = ['jpeg', 'bmp', 'png', 'gif', 'jpg']

    def allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in self.image_type

    def get(self):
        rtn = RtnMessage()
        try:
            data = {
                "question_type_id": request.args.get('question_type_id', None),
                "type_id": request.args.get('type_id', None),
                "difficulty": request.args.get('difficulty', None),
                "category": request.args.get("category", None)
            }
            dao = QuestionQuery(config)
            df = dao.get_question_type()
            df['type'] = df['type'].astype(str)
            type_name_list = df['type_name'].to_list()
            if data['difficulty']:
                df_2 = dao.get_difficulty_type()
                if not (df_2['type'].astype(str) == data['difficulty']).any():
                    raise Exception('difficulty invalid')

            if data['category']:
                df_2 = dao.get_question_category()
                if not (df_2['type'].astype(str) == data['category']).any():
                    raise Exception('category invalid')

            if data['question_type_id']:
                if not (df['type'] == data['question_type_id']).any():
                    raise Exception('invalid question_type_id')
                question_type = df[df['type'] == data['question_type_id']]['type_name'].to_list()[0].lower()
                df = dao.get_question_by_question_type(question_type=question_type,
                                                       difficulty=data['difficulty'],
                                                       category=data['category'])

            if data['type_id']:
                df_2 = dao.get_question_type_by_type_id(type_name_list=type_name_list,
                                                        type_id=data['type_id'])
                if not len(df_2):
                    raise Exception('invalid type_id')
                df = dao.get_question_by_type_id(table_name=df_2['type1'][0].lower(),
                                                 category=data['category'],
                                                 difficulty=data['difficulty'],
                                                 type_id=data['type_id'])

            if not data['question_type_id'] and not data['type_id']:
                df = dao.get_all_question(table_list=type_name_list,
                                          category=data['category'],
                                          difficulty=data['difficulty'])

            for index, row in df.iterrows():
                rtn.result.append(
                    {
                        "question": {
                            "uid": row['uuid'],
                            "question": row['question'],
                            "options1": row['options1'],
                            "options2": row['options2'],
                            "options3": row['options3'],
                            "options4": row['options4'],
                            "options5": row['options5'],
                            "answer": row['answer'],
                            "type_id": row['type_id'],
                            "difficulty": row['difficulty'],
                            "image_path": row['image_path'],
                            "category": row['category'],
                        }
                    }
                )
        except Exception as e:
            self.logger.error(repr(e))
            rtn.state = False
            rtn.msg = str(e)

        return rtn.to_dict()

    def post(self):
        rtn = RtnMessage()
        try:
            data = {
                "question": request.form['question'],
                "options1": request.form['options1'],
                "options2": request.form['options2'],
                "options3": request.form.get('options3') or None,
                "options4": request.form.get('options4') or None,
                "options5": request.form.get('options5') or None,
                "answer": request.form['answer'],
                "type": request.form['type'],
                "difficulty": request.form['difficulty'],
                "image": request.files.get('image') or None,
                "category": request.form['category']
            }
            if not data["question"] or not data["options1"] or not data["options2"] or not data["answer"] \
                    or not data["type"] or not data["difficulty"] or not data["category"]:
                raise Exception('input missing')

            dao = QuestionQuery(config)
            type_list = data['type'].split(',')
            df = dao.get_question_type()
            type_id = \
                dao.get_question_class_id(class_type=df['type_name'].to_list(), type_list=type_list)['uuid'].values[0]
            if not len(df):
                raise Exception('type cannot found in db')

            df = dao.get_difficulty_type()
            if not (df['type'].astype(str) == data['difficulty']).any():
                raise Exception('difficulty invalid')

            df = dao.get_question_category()
            if not (df['type'].astype(str) == data['category']).any():
                raise Exception('category invalid')
            df['type'] = df['type'].astype(str)

            # checking answer format and type
            answer_list = data['answer'].split(',')
            for answer in answer_list:
                if len(answer) > 1 or not answer.isdigit() or int(answer) > 5:
                    raise Exception('answer format error')

            if not data['category'] in df['type'].values:
                raise Exception('category invalid')

            if (df.loc[df['category'] == '單選']['type'].values == data['category']).any():
                if len(answer_list) > 1:
                    raise Exception(f'invalid answer, expect:{"單選"}')
            else:
                if not 1 < len(answer_list) <= 5:
                    raise Exception(f'invalid answer, expect:{"多選"}')
            uid = uuid.uuid4()

            # image_save
            image_path = None
            if data['image'] and data['image'] != '':
                if not self.allowed_file(data['image'].filename):
                    raise Exception(f'invalid file type, expect:{self.image_type}')
                image_path = f'./question_image/{uid}.{data["image"].filename.rsplit(".", 1)[1].lower()}'
                data['image'].save(image_path)

            dao.insert_question(
                uid=uid,
                question=data['question'],
                options1=data['options1'],
                options2=data['options2'],
                options3=data['options3'],
                options4=data['options4'],
                options5=data['options5'],
                answer=data['answer'],
                type_id=type_id,
                difficulty=data['difficulty'],
                image_path=image_path,
                category=data['category'],
                table_name=type_list[0]
            )

        except Exception as e:
            self.logger.error(repr(e))
            rtn.state = False
            rtn.msg = str(e)

        return rtn.to_dict()

    def put(self):
        rtn = RtnMessage()
        try:
            data = {
                "question": request.form['question'],
                "options1": request.form['options1'],
                "options2": request.form['options2'],
                "options3": request.form.get('options3', None),
                "options4": request.form.get('options4', None),
                "options5": request.form.get('options5', None),
                "answer": request.form['answer'],
                "difficulty": request.form['difficulty'],
                "image": request.files.get('image', None),
                "category": request.form['category'],
                "uid": request.form['uid'],
                "question_type_id": request.form['question_type_id']
            }
            if not data["question"] or not data["options1"] or not data["options2"] or not data["answer"] \
                    or not data["difficulty"] or not data["category"] or not data['uid']:
                raise Exception('input missing')

            if len(data["question"]) >= 200 or len(data["options1"]) >= 100 or len(data["options2"]) >= 100 \
                    or len(data["options3"]) >= 100 or len(data["options4"]) >= 100 or len(data["options5"]) >= 100:
                raise Exception('input length too large')

            dao = QuestionQuery(config)

            # check type is in db
            df = dao.get_question_type()

            if not (df['type'].values.astype(str) == data['question_type_id']).any():
                raise Exception('invalid type id')
            type_name = df[df['type'].astype(str) == data['question_type_id']]['type_name'].to_list()[0].lower()

            # check question is in db
            df = dao.get_question_by_uid(uid=data['uid'], table=type_name.lower())
            if not len(df):
                raise Exception('uid not found in db')

            df = dao.get_difficulty_type()
            if not (df['type'].astype(str) == data['difficulty']).any():
                raise Exception('difficulty invalid')

            df = dao.get_question_category()
            if not (df['type'].astype(str) == data['category']).any():
                raise Exception('category invalid')

            # checking answer format and type
            answer_list = data['answer'].split(',')
            for answer in answer_list:
                if len(answer) > 1 or not answer.isdigit() or int(answer) > 5:
                    raise Exception('answer format error')


            if (df.loc[df['category'] == '單選']['type'].astype(str).values == data['category']).any():
                if len(answer_list) > 1:
                    raise Exception(f'invalid answer, expect:{"單選"}')
            else:
                if not 1 < len(answer_list) <= 5:
                    raise Exception(f'invalid answer, expect:{"多選"}')

            # image_save
            image_path = None
            for i in self.image_type:
                path = f'./question_image/{data["uid"]}.{i}'
                if os.path.exists(path):
                    os.remove(path)
            if data['image'] and data['image'] != '':
                if not self.allowed_file(data['image'].filename):
                    raise Exception(f'invalid file type, expect:{self.image_type}')
                image_path = f'./question_image/{data["uid"]}.{data["image"].filename.rsplit(".", 1)[1].lower()}'
                data['image'].save(image_path)

            updated_on = datetime.datetime.now()
            dao.update_question_by_uid(
                uid=data['uid'],
                question=data['question'],
                options1=data['options1'],
                options2=data['options2'],
                options3=data['options3'],
                options4=data['options4'],
                options5=data['options5'],
                answer=data['answer'],
                difficulty=data['difficulty'],
                image_path=image_path,
                category=data['category'],
                table_name=type_name,
                updated_on=updated_on
            )

        except Exception as e:
            self.logger.error(repr(e))
            rtn.state = False
            rtn.msg = str(e)

        return rtn.to_dict()

    def delete(self):
        rtn = RtnMessage()
        try:
            data = {
                "uid": request.json['uid'],
                "question_type_id": request.json['question_type_id']
            }
            dao = QuestionQuery(config)
            df = dao.get_question_type()
            df['type'] = df['type'].astype(str)

            if not (df['type'].values == data['question_type_id']).any():
                raise Exception('invalid type id')
            type_name = df[df['type'] == data['question_type_id']]['type_name'].to_list()[0].lower()
            dao.delete_question_by_uid(uid=data['uid'], table_name=type_name)

            for i in self.image_type:
                path = f'./question_image/{data["uid"]}.{i}'
                if os.path.exists(path):
                    os.remove(path)
        except Exception as e:
            self.logger.error(repr(e))
            rtn.state = False
            rtn.msg = str(e)

        return rtn.to_dict()
