import os
import json
import re
import fitz  # PyMuPDF
from database.db import get_connection
from database.paper import Paper


def remove_hyphenation(text):
    """
    去掉跨行的连字符但保留单词内部的连字符。
    """
    # 识别跨行连字符并合并单词，但不合并 `-` 后面有字母的情况
    text = re.sub(r'(\w+)-\s+(\w+)', r'\1\2', text)
    text = re.sub(r'stateof-the-art', 'state-of-the-art', text)
    return text


def extract_section_from_pdf(pdf_path, start_marker, end_marker):
    doc = fitz.open(pdf_path)
    section_text = ""
    section_started = False

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        page_text = page.get_text()

        if start_marker in page_text:
            section_started = True
            start_index = page_text.index(start_marker) + len(start_marker)
            page_text = page_text[start_index:]

        if section_started:
            if end_marker in page_text:
                end_index = page_text.index(end_marker)
                section_text += page_text[:end_index]
                break
            else:
                section_text += page_text

    # 清理文本，去除多余的空格和换行符
    section_text = re.sub(r'\s+', ' ', section_text).strip()

    # 去掉跨行的连字符，但保留单词内部的连字符
    section_text = remove_hyphenation(section_text)

    return section_text


def extract_abstract_from_pdf(pdf_path):
    return extract_section_from_pdf(pdf_path, "Abstract", "1. Introduction")


def extract_introduction_from_pdf(pdf_path):
    return extract_section_from_pdf(pdf_path, "1. Introduction", "2.")


def extract_conclusion_from_pdf(pdf_path):
    return extract_section_from_pdf(pdf_path, "Conclusion", "References")


def process_multiple_pdfs(pdf_dir):
    conn = get_connection()
    if not conn:
        print("Failed to connect to the database")
        return
    try:
        # 获取所有论文信息
        papers = Paper.get_all_papers(conn)
        if papers is None:
            print("Failed to retrieve papers from database")
            return

        for paper in papers:
            title = paper['title']
            pdf_url = paper['url']
            file_name = paper['file_name'] or pdf_url.split('/')[-1]
            pdf_path = os.path.join(pdf_dir, file_name)

            if os.path.exists(pdf_path):
                abstract = extract_abstract_from_pdf(pdf_path)
                introduction = extract_introduction_from_pdf(pdf_path)
                conclusion = extract_conclusion_from_pdf(pdf_path)

                # 如果abstract和introduction都为空，则跳过这篇论文
                if not abstract and not introduction:
                    continue

                if abstract == "" and introduction == "":
                    continue

                # 更新数据库
                Paper.update_paper(conn, title, abstract=abstract,
                                   introduction=introduction, conclusion=conclusion)
            else:
                print(f"File {file_name} not found in directory {pdf_dir}")

    except Exception as e:
        print(f"Error processing PDFs: {e}")
    finally:
        conn.close()


def get_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return remove_hyphenation(text)


if __name__ == "__main__":
    # # 处理PDF目录中的所有PDF文件
    pdf_directory = "../data/pdfs"
    process_multiple_pdfs(pdf_directory)
