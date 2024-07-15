import asyncio
import os
import time
import logging
from collections import deque


from database.db import get_connection
from database.classification import Classification
from tool.zhipu import get_classification_result_by_zhipu, get_classification_response_by_zhipu_async, check_zhipu_async_classification_result
from database.paper import Paper

log_file = '../logs/classification.log'
os.makedirs(os.path.dirname(log_file), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_file,
    filemode='a'
)


def process_result(result):
    # 处理result
    is_applicable = 'Y' in result[0]
    if is_applicable: is_applicable = 'Y'
    sub_domain = ""
    reason = ""
    if is_applicable == 'Y':
        sub_domain = result[1].split("[")[1].split("]")[0]
        reason = result[2].split("[")[1].split("]")[0]
    dict_result = {"is_applicable": is_applicable, "sub_domain": sub_domain, "reason": reason}
    return dict_result


# def classify_by_zhipu():
#     conn = get_connection()
#     papers = Paper.get_all_papers(conn)
#     for paper in papers:
#         if paper['abstract'] is None or paper['abstract'] == '':
#             continue
#         content = f"title: {paper['title']}; abstract: {paper['abstract']}"
#
#         max_retries = 10
#         retry_delay = 1  # 秒
#
#         for attempt in range(max_retries):
#             try:
#                 result = get_result_by_zhipu(content=content)
#                 dict_result = process_result(result)
#                 Classification.classify(conn, paper['title'], is_applicable=dict_result["is_applicable"],
#                                         sub_domain=dict_result["sub_domain"],
#                                         classification_reason=dict_result["reason"], model="zhipu")
#                 break  # 如果成功，跳出重试循环
#             except Exception as e:
#                 if attempt < max_retries - 1:  # 如果不是最后一次尝试
#                     logging.error(f"处理论文 '{paper['title']}' 失败，正在重试。错误: {str(e)}")
#                     time.sleep(retry_delay)  # 等待一段时间后重试
#                 else:
#                     logging.error(f"处理论文 '{paper['title']}' 失败，达到最大重试次数。错误: {str(e)}")
#                     # 这里可以选择记录失败的论文，以便后续处理
#     conn.close()


def classify_by_zhipu(datas, max_sync=10, wait_time=1, max_retries=10):
    queue = deque()
    data_index = 0
    conn = get_connection()

    def add_to_queue():
        nonlocal data_index
        while len(queue) < max_sync and data_index < len(datas):
            data = datas[data_index]
            response = get_classification_response_by_zhipu_async(data['content'])
            queue.append((response, data, 0))  # 0 is the retry count
            data_index += 1

    while queue or data_index < len(datas):
        add_to_queue()

        if not queue:
            continue

        time.sleep(wait_time)
        response, data, retry_count = queue.popleft()

        try:
            result = check_zhipu_async_classification_result(response)
            if result is None:  # Failed
                if retry_count < max_retries:
                    logging.warning(f"处理内容失败，正在重试。重试次数: {retry_count + 1}")
                    new_response = get_classification_response_by_zhipu_async(data['content'])
                    queue.append((new_response, data, retry_count + 1))
                else:
                    logging.error(f"处理内容失败，达到最大重试次数。title:{data['title']}")
            elif not result:  # Still processing
                queue.append((response, data, retry_count))
            else:  # Success
                print(result)
                dict_result = process_result(result)
                Classification.classify(conn, data['title'], is_applicable=dict_result["is_applicable"],
                                        sub_domain=dict_result["sub_domain"],
                                        classification_reason=dict_result["reason"], model="zhipu")
                logging.info(f"处理内容成功。title:{data['title']}")
        except Exception as e:
            if retry_count < max_retries:
                logging.error(f"处理内容时发生错误，正在重试。错误: {str(e)}, title:{data['title']}")
                queue.append((response, data, retry_count + 1))
            else:
                logging.error(f"处理内容失败，达到最大重试次数。错误: {str(e)}, title:{data['title']}")

    conn.close()


def get_datas_from_db():
    conn = get_connection()
    papers = Paper.get_all_papers(conn, limit=100, offset=1200)
    datas = []
    for paper in papers:
        if paper['abstract'] is None or paper['abstract'] == '':
            continue
        content = f"title: {paper['title']}; abstract: {paper['abstract']}"
        datas.append({'title': paper['title'], 'content': content})
    conn.close()
    return datas


if __name__ == '__main__':
    datas = get_datas_from_db()
    classify_by_zhipu(datas, max_sync=10, wait_time=1, max_retries=10)
