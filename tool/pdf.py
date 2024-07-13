import os
import json
import re
import fitz  # PyMuPDF


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


def process_multiple_pdfs(pdf_dir, paper_links_json, output_json):
    with open(paper_links_json, 'r', encoding='utf-8') as f:
        paper_links = json.load(f)

    sections = []

    for paper in paper_links:
        title = paper['title']
        pdf_url = paper['pdf_url']
        file_name = pdf_url.split('/')[-1]
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

            sections.append({
                "title": title,
                "file_name": file_name,
                "abstract": abstract,
                "introduction": introduction,
                "conclusion": conclusion
            })
        else:
            print(f"File {file_name} not found in directory {pdf_dir}")

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(sections, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    # # 处理PDF目录中的所有PDF文件
    pdf_directory = "../data/pdfs"
    paper_links_file = "../data/paper_links.json"
    output_file = "../data/papers.json"
    process_multiple_pdfs(pdf_directory, paper_links_file, output_file)
    # with open('../data/papers.json', 'r', encoding='utf-8') as f:
    #     papers = json.load(f)
    #     print(len(papers))
