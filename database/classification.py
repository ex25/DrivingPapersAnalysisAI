import logging
import os

log_file = '../logs/download.log'
os.makedirs(os.path.dirname(log_file), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_file,
    filemode='a'
)


class Classification:
    @staticmethod
    def classify(conn, title, is_applicable=None, sub_domain=None, classification_reason=None, model="zhipu"):
        try:
            with conn.cursor() as cursor:
                # 首先检查是否存在对应的 title
                check_sql = "SELECT COUNT(*) FROM paper_classifications WHERE title = %s"
                cursor.execute(check_sql, (title,))
                exists = cursor.fetchone()[0]

                if exists:
                    # 如果存在，执行更新操作
                    update_sql = (f"UPDATE paper_classifications SET is_applicable_{model} = %s, "
                                  f"subdomain_{model} = %s, classification_reason_{model} = %s "
                                  f"WHERE title = %s")
                    cursor.execute(update_sql, (is_applicable, sub_domain, classification_reason, title))
                else:
                    # 如果不存在，执行插入操作
                    insert_sql = (f"INSERT INTO paper_classifications (title, is_applicable_{model}, "
                                  f"subdomain_{model}, classification_reason_{model}) "
                                  f"VALUES (%s, %s, %s, %s)")
                    cursor.execute(insert_sql, (title, is_applicable, sub_domain, classification_reason))

                conn.commit()
                logging.info(f"Successfully {'updated' if exists else 'inserted'} classification for title: {title}")
        except Exception as e:
            conn.rollback()
            logging.error(f"Error {'updating' if exists else 'inserting'} classification for title {title}: {e}")

    @staticmethod
    def get_classification_by_title(conn, title, model="zhipu"):
        try:
            with conn.cursor() as cursor:
                # 首先检查是否存在对应的 title
                check_sql = (f"SELECT is_applicable_{model}, subdomain_{model}, classification_reason_{model} "
                             f"FROM paper_classifications WHERE title = %s")
                cursor.execute(check_sql, (title,))
                result = cursor.fetchone()
                if result:
                    return result
                else:
                    return None
        except Exception as e:
            logging.error(f"Error getting classification for title {title}: {e}")

    @staticmethod
    def get_classification_results(conn, model="zhipu"):
        try:
            with conn.cursor() as cursor:
                # 获取论文总数

                paper_count_sql = f"SELECT COUNT(*) FROM paper_classifications WHERE is_applicable_{model} IS NOT NULL"
                cursor.execute(paper_count_sql)
                paper_count = cursor.fetchone()[0]
                # 计算能用于智能驾驶的论文数
                applicable_paper_count_sql = (f"SELECT COUNT(*) FROM paper_classifications "
                                              f"WHERE is_applicable_{model} = 'Y'")
                cursor.execute(applicable_paper_count_sql)
                applicable_paper_count = cursor.fetchone()[0]

                # 获取各个分类的论文数
                classification_count_sql = (f"SELECT subdomain_{model}, COUNT(*) AS count "
                                            f"FROM paper_classifications "
                                            f"WHERE is_applicable_{model} = 'Y'"
                                            f"GROUP BY subdomain_{model}")
                cursor.execute(classification_count_sql)
                classification_count = cursor.fetchall()
                classification_results = []
                for classification in classification_count:
                    classification_results.append({"subdomain": classification[0], "count": classification[1]})

        except Exception as e:
            logging.error(f"Error getting classification results: {e}")
            return None

        return {"paper_count": paper_count, "applicable_paper_count": applicable_paper_count,
                "classification_results": classification_results}
