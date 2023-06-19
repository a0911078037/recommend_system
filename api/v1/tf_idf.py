from flask_restx import Resource
from flask import request
from utility.RtnMessage import RtnMessage
from app import config
from data_access.query.question_query import QuestionQuery
from utility.logger import get_logger
from ckiptagger import data_utils, WS, construct_dictionary
import os
import pandas as pd
import numpy as np


ws = WS('./model/tf_idf/data', disable_cuda=False)


class TF_IDF(Resource):
    logger = get_logger('TF-IDF')

    def get(self):
        rtn = RtnMessage()
        data = None
        try:
            pass

        except Exception as e:
            self.logger.error(e, exc_info=True)
            self.logger.error(f"REQUEST PARAM: {data}")
            rtn.state = False
            rtn.msg = str(e)

        return rtn.to_dict()

    def post(self):
        rtn = RtnMessage()
        data = None
        try:
            # folder and model check
            if not os.path.exists('./model'):
                os.mkdir('./model')
            if not os.path.exists('./model/tf_idf'):
                os.mkdir('./model/tf_idf')
            if not os.path.exists('./model/tf_idf/data'):
                data_utils.download_data_gdown("./model/tf_idf")
                os.remove('./model/tf_idf/data.zip')

            # get all question and replace with \n
            dao = QuestionQuery(config)
            question_type_list = dao.get_question_type()['type_name'].to_list()
            question_df = dao.get_all_question(table_list=question_type_list)
            question_id = question_df['uuid']
            question_df = question_df[['question', 'options1', 'options2', 'options3', 'options4', 'options5']]
            question_df.fillna('', inplace=True)
            question_list = question_df.values.tolist()
            question_list = ['\n'.join(x) for x in question_list]
            question_id_list = question_id.values.tolist()
            similarity_df = pd.DataFrame(columns=question_id_list, index=question_id_list)
            recommend_dict = {
                "JavaScript": 1,
                "HTML5": 1,
            }
            recommend_dict = construct_dictionary(recommend_dict)
            # 斷詞標註
            word_sentence_list = ws(
                question_list,
                recommend_dictionary=recommend_dict
                # sentence_segmentation = True, # To consider delimiters
            )
            tf_idf_model = TF_IDF_Model(word_sentence_list)
            for i, word_sentence in enumerate(word_sentence_list):
                score = tf_idf_model.get_documents_score(word_sentence)
                similarity_df[question_id_list[i]] = score

            print(similarity_df)
            similarity_df.to_csv('./temp/result.csv')

        except Exception as e:
            self.logger.error(e, exc_info=True)
            self.logger.error(f"REQUEST PARAM: {data}")
            rtn.state = False
            rtn.msg = str(e)

        return rtn.to_dict()


class TF_IDF_Model(object):
    def __init__(self, documents_list):
        self.documents_list = documents_list
        self.documents_number = len(documents_list)
        self.tf = []
        self.idf = {}
        self.init()

    def init(self):
        df = {}
        for document in self.documents_list:
            temp = {}
            for word in document:
                temp[word] = temp.get(word, 0) + 1/len(document)
            self.tf.append(temp)
            for key in temp.keys():
                df[key] = df.get(key, 0) + 1
        for key, value in df.items():
            self.idf[key] = np.log(self.documents_number / (value + 1))

    def get_score(self, index, query):
        score = 0.0
        for q in query:
            if q not in self.tf[index]:
                continue
            score += self.tf[index][q] * self.idf[q]
        return score

    def get_documents_score(self, query):
        score_list = []
        for i in range(self.documents_number):
            score_list.append(self.get_score(i, query))
        score_list = [((x-min(score_list))/(max(score_list)-min(score_list))) for x in score_list]
        return score_list

