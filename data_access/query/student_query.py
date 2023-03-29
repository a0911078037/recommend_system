from data_access.db_connect.MySQL import mysqlDB


class StudentQuery:
    def __init__(self, config):
        self._config = config
        self._db_handler = mysqlDB(config, 2)

    def create_students(self, user_id=''):
        try:
            sql = \
                f"""
                INSERT INTO student_status(user_id)
                VALUES(?)
                """
            data = (user_id)
            self._db_handler.insert(sql, data)

            sql = \
                f"""
                CREATE TABLE `{user_id}_answer` (
                `question_id` varchar(36) NOT NULL,
                `answer_time` int NOT NULL,
                `correct` tinyint NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
                """
            self._db_handler.insert(sql)

            sql = \
                f"""
                CREATE TABLE `{user_id}_paper` (
                `paper_index` int NOT NULL,
                `question_id` varchar(36) NOT NULL,
                `answer` varchar(10) NOT NULL,
                `correct` tinyint NOT NULL,
                `question_count` int NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
                """
            self._db_handler.insert(sql)

        except Exception as e:
            raise e

    def delete_student(self, user_id=''):
        try:
            sql = \
                f"""
                DELETE FROM student_status
                WHERE user_id = "{user_id}"
                """
            self._db_handler.delete(sql)

            sql = \
                f"""
                DROP TABLE `{user_id}_answer`
                """
            self._db_handler.delete(sql)

            sql = \
                f"""
                DROP TABLE `{user_id}_paper`
                """
            self._db_handler.delete(sql)
        except Exception as e:
            raise e