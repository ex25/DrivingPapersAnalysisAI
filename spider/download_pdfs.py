import asyncio
import httpx
import json
import os
from tqdm import tqdm
import logging
import random
from fake_useragent import UserAgent

# 设置日志
log_file = '../logs/download.log'
os.makedirs(os.path.dirname(log_file), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_file,
    filemode='a'
)

# 创建UserAgent对象
ua = UserAgent()

# 定义一些请求头
HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Upgrade-Insecure-Requests': '1',
}


async def download_pdf(client, title, url, semaphore, path="../data/pdfs", max_retries=5):
    async with semaphore:
        for attempt in range(max_retries):
            try:
                # 随机生成User-Agent
                headers = HEADERS.copy()
                headers['User-Agent'] = ua.random

                # 随机延迟
                await asyncio.sleep(random.uniform(1, 3))

                response = await client.get(url, headers=headers, timeout=60.0)
                if response.status_code == 200:
                    filename = url.split('/')[-1]
                    with open(os.path.join(path, filename), "wb") as f:
                        f.write(response.content)
                    logging.info(f"Downloaded: {filename}")
                    return f"Downloaded: {filename}"
                else:
                    logging.warning(f"Failed to download {title}: HTTP {response.status_code}. Retrying...")
            except httpx.RequestError as e:
                logging.error(f"Request error for {title}: {str(e)}. Retrying...")
            except Exception as e:
                logging.error(f"Unexpected error for {title}: {str(e)}. Retrying...")

            if attempt < max_retries - 1:
                # 使用退避策略
                await asyncio.sleep(random.uniform(2 * attempt, 2 * (attempt + 1)))

        logging.error(f"Failed to download {title} after {max_retries} attempts")
        return f"Failed to download {title} after {max_retries} attempts"


async def main():
    os.makedirs("../data/pdfs", exist_ok=True)

    with open("../data/paper_links.json", "r", encoding="utf-8") as f:
        papers = json.load(f)

    # 随机打乱顺序
    random.shuffle(papers)

    semaphore = asyncio.Semaphore(10) # 并发数10

    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        tasks = [download_pdf(client, paper['title'], paper['pdf_url'], semaphore) for paper in papers]

        results = []
        for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Downloading PDFs"):
            result = await f
            results.append(result)

            # 在每次下载完成后添加一个随机的长暂停，以避免被服务器拉黑
            if random.random() < 0.05: # 5%的概率
                pause_time = random.uniform(3, 5)
                logging.info(f"Taking a break for {pause_time:.2f} seconds...")
                await asyncio.sleep(pause_time)

    success = sum(1 for r in results if r.startswith("Downloaded"))
    failed = len(results) - success
    logging.info(f"Download complete. Success: {success}, Failed: {failed}")

    for result in results:
        if not result.startswith("Downloaded"):
            logging.error(result)


if __name__ == "__main__":
    asyncio.run(main())