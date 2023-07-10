from flask_restx import Resource
from flask import request
from utility.RtnMessage import RtnMessage
from app import config
from data_access.query.question_query import QuestionQuery
from utility.logger import get_logger
from ckiptagger import data_utils, WS, construct_dictionary, POS, NER
import os
import pandas as pd
import numpy as np

# folder and model check
if not os.path.exists('./model'):
    os.mkdir('./model')
if not os.path.exists('./model/tf_idf'):
    os.mkdir('./model/tf_idf')
if not os.path.exists('./model/tf_idf/data'):
    data_utils.download_data_gdown("./model/tf_idf")
    os.remove('./model/tf_idf/data.zip')
if not bool(int(config['API']['DEBUG'])):
    ws = WS('./model/tf_idf/data', disable_cuda=False)
    pos = POS('./model/tf_idf/data', disable_cuda=False)


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
            # get all question and replace with \n
            dao = QuestionQuery(config)
            question_type_list = dao.get_question_type()['type_name'].to_list()
            question_df = dao.get_all_question(table_list=question_type_list)
            question_id = question_df['uuid']
            question_df_full = question_df[['options1', 'options2', 'options3', 'options4', 'options5', 'answer']]
            question_df = question_df[['question']]
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
                recommend_dictionary=recommend_dict,
                sentence_segmentation=True
                # sentence_segmentation = True, # To consider delimiters
            )
            word_pos_list = pos(word_sentence_list)
            stop_pos = {'Nep', 'Nh', 'Nb'}
            short_sentence_list = []
            # 停用詞刪除
            for pos_list, word_list in zip(word_pos_list, word_sentence_list):
                temp = []
                for word_pos, word in zip(pos_list, word_list):
                    # 只留名詞和動詞
                    is_N_or_V = word_pos.startswith("V") or word_pos.startswith("N") or word_pos == 'FW'
                    # 去掉名詞裡的某些詞性
                    is_not_stop_pos = word_pos not in stop_pos
                    # 只剩一個字的詞也不留
                    is_not_one_charactor = not (len(word) == 1)
                    # 組成串列
                    if is_N_or_V and is_not_stop_pos and is_not_one_charactor:
                        temp.append(f"{word}")
                short_sentence_list.append(temp)
            short_sentence_df = pd.DataFrame(data=short_sentence_list)
            short_sentence_df = pd.concat([short_sentence_df, question_df_full], axis=1)
            short_sentence_df.to_csv('./short_question.csv', encoding="utf_8_sig")
            question_df.to_csv('./question.csv', encoding="utf_8_sig")

            rtn.result = short_sentence_list
            # tf_idf_model = TF_IDF_Model(word_sentence_list)
            # for i, word_sentence in enumerate(word_sentence_list):
            #     score = tf_idf_model.get_documents_score(word_sentence)
            #     similarity_df[question_id_list[i]] = score
            #
            # print(similarity_df)
            # similarity_df.to_csv('./temp/result.csv')

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
                temp[word] = temp.get(word, 0) + 1 / len(document)
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
        score_list = [((x - min(score_list)) / (max(score_list) - min(score_list))) for x in score_list]
        return score_list
