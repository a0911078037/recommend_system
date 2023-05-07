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

    def get_question(self, question_name_list=None, student_id=None, pick_num=None):
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
                    WHERE t2.question_id IS NULL LIMIT {pick_num};
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

    def insert_student_paper(self, student_id=None, paper_index=None, question_id_list=None, answer_list=None,
                             correct_list=None, student_answer_list=None):
        try:
            sql = \
                f"""
                INSERT INTO `{student_id}_paper`
                (paper_index, question_id, answer, correct, student_answer)
                VALUES(?,?,?,?,?);
                """
            data_list = []
            for question, answer, correct, student_answer in zip(question_id_list, answer_list, correct_list,
                                                                 student_answer_list):
                data_list.append((paper_index, question, answer, correct, student_answer))

            self._db_handler_student.execute_many(sql, data_list)
        except Exception as e:
            raise e

    def insert_student_answer(self, student_id=None, correct_list=None, question_id_list=None):
        try:
            sql = \
                f"""
                INSERT INTO `{student_id}_answer`
                (question_id, answer_time, correct)
                VALUES(?,?,?)
                ON DUPLICATE KEY UPDATE
                answer_time = answer_time + 1,
                correct = ?
                """
            data_list = [(question, 1, correct, correct) for question, correct in zip(question_id_list, correct_list)]
            self._db_handler_student.execute_many(sql, data_list)
        except Exception as e:
            raise e

    def insert_student_paper_status(self, student_id=None, paper_index=None, paper_id=None, answered_right=None,
                                    total_question=None, created_on=None):
        try:
            sql = \
                f"""
                INSERT INTO `{student_id}_status`
                (paper_index, paper_id, answered_right, total_question, created_on)
                VALUES(?,?,?,?,?)
                """
            data = (paper_index, paper_id, answered_right, total_question, created_on)
            self._db_handler_student.insert(sql, data)
        except Exception as e:
            raise e

    def get_question_type_id(self, question_name_list=None):
        try:
            sql = ''
            for question_name in question_name_list:
                sql += \
                    f"""
                    SELECT uuid, type1 from `{question_name}_type`
                    UNION ALL"""
            sql = sql[0:-9]
            df = self._db_handler_question.execute_dataframe(sql)
            return df
        except Exception as e:
            raise e

    def update_student_status(self, student_id=None, counter_list=None, question_name_list=None):
        try:
            sql = \
            f"""
            UPDATE `student_status`
            SET 
            """
            for question_name in question_name_list:
                sql += f"correct_{question_name} = correct_{question_name} + {counter_list[f'correct_{question_name}']}, " \
                       f"answer_{question_name} = answer_{question_name} + {counter_list[f'{question_name}']}, "

            sql = sql[0:-2]
            sql += f" WHERE student_id = '{student_id}'"
            self._db_handler_student.update(sql)
        except Exception as e:
            raise e
