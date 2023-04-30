import pandas as pd

from data_access.db_connect.MySQL import mysqlDB


class TestQuery:
    def __init__(self, config):
        self._config = config
        self._db_handler_question = mysqlDB(config, 1)
        self._db_handler_student = mysqlDB(config, 2)

    def get_question_type(self):
        try:
            sql = \
                f"""
                SELECT * FROM question_type
                """
            df = self._db_handler_question.execute_dataframe(sql)
            return df
        except Exception as e:
            raise e

    def get_question(self, question_name_list=None, student_id=None):
        try:
            data_frame = pd.DataFrame()
            for question_type in question_name_list:
                sql = \
                    f"""
                    SELECT t1.uuid, t1.question, t1.options1, t1.options2, t1.options3, t1.options4, t1.options5, 
                    t1.answer, t1.type_id, t1.category FROM recommend_system.{question_type}_questions AS t1
                    LEFT JOIN student_base.`{student_id}_answer` AS t2 ON 
                    t1.uuid=t2.question_id AND
                    t2.correct = 1
                    WHERE t2.question_id IS NULL;
                    """
                df = self._db_handler_question.execute_dataframe(sql)
                data_frame = data_frame.append(df, ignore_index=True)
            return data_frame
        except Exception as e:
            raise e

    def get_new_paperIndex(self, student_id=None):
        try:
            sql = \
                f"""
                SELECT MAX(paper_index) as p_index FROM student_base.`{student_id}_status`;
                """
            df = self._db_handler_student.execute_dataframe(sql)
            if not df['p_index'][0]:
                return 0
            return df['p_index'][0]
        except Exception as e:
            raise e
