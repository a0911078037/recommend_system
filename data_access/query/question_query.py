from data_access.db_connect.MySQL import mysqlDB
from utility.logger import get_logger


class QuestionQuery:
    def __init__(self, config):
        self._config = config
        self._db_handler = mysqlDB(config, 1)
        self.logger = get_logger('QuestionQuery')

    def insert_question(self, question=None, options1=None, options2=None, options3=None, options4=None, options5=None,
                        answer=None, type_id=None, difficulty=None, image_path=None, category=None, table_name=None,
                        uid=None):
        try:
            sql = \
                f"""
                INSERT INTO {table_name}_questions
                (question, options1, options2, options3, options4, options5, answer, type_id, difficulty,
                image_path, category, uuid)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                """
            data = (question, options1, options2, options3, options4, options5, answer, type_id, int(difficulty),
                    image_path, int(category), str(uid))
            self._db_handler.insert(sql, data)
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: question:{question}, options1:{options1}, options2:{options2}, "
                              f"options3:{options3}, options4:{options4},options5:{options5}, answer:{answer}, "
                              f"type_id:{type_id}, difficulty:{difficulty}, image_path:{image_path}, "
                              f"category:{category}, uuid:{uid}")
            raise Exception('error in query')

    def get_question_type(self):
        try:
            sql = \
                f"""
                SELECT * FROM question_type
                """
            df = self._db_handler.execute_dataframe(sql)
            return df
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: NONE")
            raise Exception('error in query')

    def update_question_type_question_count(self, question_type=None, type_id=None):
        try:
            sql = \
                f"""
                UPDATE {question_type}_type
                SET question_count = question_count + 1
                WHERE type_id = '{type_id}'
                """
            self._db_handler.update(sql)
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: question_type: {question_type}, type_id: {type_id}")
            raise Exception('error in query')

    def delete_question_type_question_count(self, question_type=None, type_id=None):
        try:
            sql = \
                f"""
                UPDATE {question_type}_type
                SET question_count = question_count - 1
                WHERE type_id = "{type_id}"
                """
            self._db_handler.update(sql)
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: question_type: {question_type}, type_id: {type_id}")
            raise Exception('error in query')

    def get_question_class_id(self, class_type=None, type_list=None):
        try:
            sql = ''
            for c in class_type:
                sql += \
                    f"""
                    SELECT * FROM recommend_system.{c.lower()}_type
                    WHERE """
                for i, t in enumerate(type_list):
                    sql += \
                        f"""
                        type{i + 1}="{t}" and """
                sql = sql[0:-5]
                sql += \
                    f"""
                    UNION"""
            sql = sql[0:-5]
            df = self._db_handler.execute_dataframe(sql)
            return df
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: class_type: {class_type}, type_list: {type_list}")
            raise Exception('error in query')

    def get_question_type_by_type_id(self, type_name_list=None, type_id=None):
        try:
            sql = ''
            for table in type_name_list:
                sql += \
                    f"""
                    SELECT * FROM {table}_type
                    {('WHERE type_id="' + type_id + '"') if type_id else ""}
                    UNION
                    """
            sql = sql[0:-30]
            df = self._db_handler.execute_dataframe(sql)
            return df
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: type_name_list: {type_name_list}, type_id: {type_id}")
            raise Exception('error in query')

    def get_question_by_type_id(self, table_name=None, type_id=None, difficulty=None, category=None):
        try:
            sql = \
                f"""
                SELECT * FROM {table_name}_questions
                WHERE type_id="{type_id}"
                {('AND difficulty="' + difficulty + '"') if difficulty else ""}
                {('AND category="' + category + '"') if category else ""}
                """
            df = self._db_handler.execute_dataframe(sql)
            return df
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: table_name: {table_name}, type_id: {type_id}, difficulty:{difficulty}, "
                              f"category:{category}")
            raise Exception('error in query')

    def get_difficulty_type(self, type_id=None):
        try:
            sql = \
                f"""
                SELECT * FROM difficulty_type
                {('WHERE type="'+type_id+'"') if type_id else ''}
                """
            df = self._db_handler.execute_dataframe(sql)
            return df
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: type_id: {type_id}")
            raise Exception('error in query')

    def get_question_category(self):
        try:
            sql = \
                f"""
                SELECT * FROM question_category
                """
            df = self._db_handler.execute_dataframe(sql)
            return df
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: NONE")
            raise Exception('error in query')

    def get_question_by_uid(self, uid=None, table=None):
        try:
            sql = \
                f"""
                SELECT * FROM {table}_questions
                WHERE uuid="{uid}"
                """
            df = self._db_handler.execute_dataframe(sql)
            return df
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: table: {table}, uid: {uid}")
            raise Exception('error in query')

    def update_question_by_uid(self, question=None, options1=None, options2=None, options3=None, options4=None,
                               options5=None, answer=None, difficulty=None, image_path=None, category=None,
                               table_name=None, uid=None, updated_on=None):
        try:
            sql = \
                f"""
                UPDATE {table_name}_questions
                SET question="{question}", options1="{options1}", options2="{options2}", options3="{options3}", 
                options4="{options4}", options5="{options5}", answer="{answer}", difficulty="{difficulty}", 
                image_path="{image_path}", category="{category}", updated_on="{updated_on}"
                WHERE uuid="{uid}"
                """
            self._db_handler.update(sql)
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: question:{question}, options1:{options1}, options2:{options2}, "
                              f"options3:{options3}, options4:{options4},options5:{options5}, answer:{answer}, "
                              f"difficulty:{difficulty}, image_path:{image_path}, category:{category}, uuid:{uid}")
            raise Exception('error in query')

    def delete_question_by_uid(self, uid=None, table_name=None):
        try:
            sql = \
                f"""
                DELETE FROM {table_name}_questions
                WHERE uuid="{uid}"
                """
            self._db_handler.delete(sql)
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: table_name:{table_name}, uid:{uid}")
            raise Exception('error in query')

    def get_all_question(self, table_list=None, difficulty=None, category=None):
        try:
            sql = ''
            for table in table_list:
                sql += \
                    f"""
                    SELECT * FROM {table}_questions
                    {"WHERE" if difficulty or category else ''}
                    {("difficulty=" + difficulty) if difficulty else ''}
                    {"and" if difficulty and category else ''}
                    {("category=" + category) if category else ''}
                    UNION
                    """
            sql = sql[0:-30]
            df = self._db_handler.execute_dataframe(sql)
            return df
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: table_list:{table_list}, difficulty:{difficulty}, category:{category}")
            raise Exception('error in query')

    def get_question_by_question_type(self, question_type=None, difficulty=None, category=None):
        try:
            sql = \
                f"""
                SELECT * FROM {question_type}_questions
                {"WHERE" if difficulty or category else ''}
                {("difficulty=" + difficulty) if difficulty else ''}
                {"and" if difficulty and category else ''}
                {("category=" + category) if category else ''}
                """
            df = self._db_handler.execute_dataframe(sql)
            return df
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: question_type:{question_type}, difficulty:{difficulty}, category:{category}")
            raise Exception('error in query')

    def get_question_type_id(self):
        pass
