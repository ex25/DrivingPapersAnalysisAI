class Paper:
    @staticmethod
    def get_all_papers(conn):
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM papers")
                datas = cur.fetchall()
                papers = []
                for row in datas:
                    dic = {"title": row[1], "url": row[2], "file_name": row[3],
                           "abstract": row[4], "introduction": row[5], "conclusion": row[6]}
                    papers.append(dic)

        except Exception as e:
            print(e)
            return None
        return papers

    @staticmethod
    def get_paper_by_title(conn, title):
        try:
            with conn.cursor() as cur:
                cur = conn.cursor()
                cur.execute("SELECT * FROM papers WHERE title=%s", (title,))
                data = cur.fetchone()
                if data is None:
                    return None
                paper = [{"title": data[1], "url": data[2], "file_name": data[3],
                         "abstract": data[4], "introduction": data[5], "conclusion": data[6]}]
        except Exception as e:
            print(e)
            return None
        return paper

    @staticmethod
    def add_paper(conn, title, url=None, file_name=None, abstract=None, introduction=None, conclusion=None) -> bool:
        try:
            with conn.cursor() as cur:
                fields = ['title']
                values = [title]

                if url is not None:
                    fields.append('url')
                    values.append(url)
                if file_name is not None:
                    fields.append('file_name')
                    values.append(file_name)
                if abstract is not None:
                    fields.append('abstract')
                    values.append(abstract)
                if introduction is not None:
                    fields.append('introduction')
                    values.append(introduction)
                if conclusion is not None:
                    fields.append('conclusion')
                    values.append(conclusion)

                sql = f"INSERT INTO papers ({','.join(fields)}) VALUES ({','.join(['%s'] * len(values))})"

                cur.execute(sql, tuple(values))
                conn.commit()
            return True
        except Exception as e:
            print(f"Error adding paper: {e}")
            conn.rollback()
            return False

    @staticmethod
    def delete_paper(conn, title):
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM papers WHERE title=%s", (title,))
                conn.commit()
        except Exception as e:
            print(e)
            return False
        return True

    @staticmethod
    def update_paper(conn, title, url=None, file_name=None, abstract=None, introduction=None, conclusion=None):
        try:
            with conn.cursor() as cur:
                update_fields = []
                update_values = []

                if url is not None:
                    update_fields.append("url=%s")
                    update_values.append(url)
                if file_name is not None:
                    update_fields.append("file_name=%s")
                    update_values.append(file_name)
                if abstract is not None:
                    update_fields.append("abstract=%s")
                    update_values.append(abstract)
                if introduction is not None:
                    update_fields.append("introduction=%s")
                    update_values.append(introduction)
                if conclusion is not None:
                    update_fields.append("conclusion=%s")
                    update_values.append(conclusion)

                if update_fields:
                    sql = f"UPDATE papers SET {', '.join(update_fields)} WHERE title=%s"
                    cur.execute(sql, tuple(update_values + [title]))
                    conn.commit()
                    return True
                else:
                    print("No fields to update")
                    return False
        except Exception as e:
            print(f"Error updating paper: {e}")
            conn.rollback()
            return False
