import httpx
from bs4 import BeautifulSoup
import json


def get_cvpr24_home_page():
    url = 'https://openaccess.thecvf.com/CVPR2024?day=all'
    response = httpx.get(url)
    return response.text


def get_all_paper_links(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')
    papers = []
    content_div = soup.find('div', id='content')
    # 遍历所有的dt标签
    for dt in content_div.find_all('dt', class_='ptitle'):
        # 获取论文标题
        title = dt.a.text
        # 获取下一个dd标签（包含PDF链接）
        dd = dt.find_next_sibling('dd').find_next_sibling('dd')

        # 在dd中查找PDF链接
        for a in dd.find_all('a'):
            if a.text == 'pdf':
                pdf_link = 'https://openaccess.thecvf.com' + a['href']
                papers.append({
                    "title": title,
                    "pdf_url": pdf_link
                })
                break
    return papers


def save_paper_links(papers):
    with open('data/paper_links.json', 'w', encoding='utf-8') as f:
        json.dump(papers, f, ensure_ascii=False, indent=4)
    print(f'保存成功！共{len(papers)}篇论文')


if __name__ == '__main__':
    page_content = get_cvpr24_home_page()
    papers = get_all_paper_links(page_content)
    save_paper_links(papers)

