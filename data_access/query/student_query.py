from data_access.db_connect.MySQL import mysqlDB
from utility.logger import get_logger


class StudentQuery:
    def __init__(self, config):
        self._config = config
        self._db_handler = mysqlDB(config, 2)
        self.logger = get_logger('StudentQuery')

    def create_students(self, user_id=''):
        try:
            sql = \
                f"""
                INSERT INTO student_status(student_id)
                VALUES(?)
                """
            data = (user_id)
            self._db_handler.insert(sql, data)

            sql = \
                f"""
                CREATE TABLE `{user_id}_answer` (
                `question_id` VARCHAR(36) NOT NULL,
                `answer_time` INT NOT NULL DEFAULT 0,
                `correct` TINYINT NOT NULL,
                PRIMARY KEY (`question_id`),
                UNIQUE INDEX `question_id_UNIQUE` (`question_id` ASC) VISIBLE);
                """
            self._db_handler.insert(sql)

            sql = \
                f"""
                CREATE TABLE `{user_id}_paper` (
                `paper_index` int NOT NULL,
                `question_id` varchar(36) NOT NULL,
                `answer` varchar(10) NOT NULL,
                `student_answer` varchar(10) NOT NULL,
                `correct` tinyint NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
                """
            self._db_handler.insert(sql)

            sql = \
                f"""
                CREATE TABLE `{user_id}_status` (
                `paper_index` INT NOT NULL,
                `paper_id` VARCHAR(45) NOT NULL,
                `paper_type` varchar(45) NOT NULL,
                `answered_right` INT NOT NULL,
                `total_question` INT NOT NULL,
                `score` smallint NOT NULL,
                `total_score` smallint NOT NULL,
                `created_on` DATETIME NOT NULL,
                `answered_on` DATETIME NOT NULL,
                PRIMARY KEY (`paper_index`),
                UNIQUE INDEX `paper_index_UNIQUE` (`paper_index` ASC) VISIBLE);
                """
            self._db_handler.insert(sql)

            sql = \
                f"""
                CREATE TABLE `{user_id}_type` (
                `type_id` VARCHAR(36) NOT NULL,
                `type_name` VARCHAR(45) NOT NULL,
                `type_correct` INT NOT NULL DEFAULT 0,
                `type_answer` INT NOT NULL DEFAULT 0,
                PRIMARY KEY (`type_id`),
                UNIQUE KEY `type_id_UNIQUE` (`type_id`));
                """
            self._db_handler.insert(sql)

        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: user_id: {user_id}")
            raise Exception('error in query')

    def delete_student(self, user_id=''):
        try:
            sql = \
                f"""
                DELETE FROM student_status
                WHERE student_id = "{user_id}"
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

            sql = \
                f"""
                DROP TABLE `{user_id}_status`
                """
            self._db_handler.delete(sql)

            sql = \
                f"""
                DROP TABLE `{user_id}_type`
                """
            self._db_handler.delete(sql)
        except Exception as e:
            self.logger.error(e)
            self.logger.error(f"FUNCTION PARAM: user_id: {user_id}")
            raise Exception('error in query')
