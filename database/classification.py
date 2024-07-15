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

