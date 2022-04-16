#!/usr/bin/env python
from bs4 import BeautifulSoup
import timeit
from urllib.parse import urlparse, urljoin
import asyncio
import aiohttp
from generator.xml_creater import creating_sitemap
from generator.xml_creater import pretty_print_xml


class Crawler:
    def __init__(self, url=""):
        self.new_urls = [url]
        self.processed_urls = []
        self.local_urls = []
        self.external_urls = []
        self.broken_urls = []

    def get_processed(self):
        return self.processed_urls

    def get_local(self):
        return self.local_urls

    def get_external(self):
        return self.external_urls

    def get_broken(self):
        return self.broken_urls

    def is_valid(self, url):
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    async def get_responce(self, session, url):
        async with session.get(url) as response:
            return await response.text()

    async def run(self):
        async with aiohttp.ClientSession() as session:
            while self.new_urls:
                url = self.new_urls.pop(0)
                print(f"Processing: {url}")
                try:
                    task = asyncio.create_task(self.crawl(session, url))
                    await task
                except Exception as e:
                    self.broken_urls.append(url)
                    print(f"Failed: {url}")
                    print(f"Error: {e}")
                finally:
                    self.processed_urls.append(url)

    async def crawl(self, session, url):
        base = urlparse(url).netloc
        response = await self.get_responce(session, url)
        soup = BeautifulSoup(response, "lxml")
        for a_tag in soup.find_all("a"):
            link = a_tag.get("href")
            if link and link.startswith("/"):
                link = urljoin(url, link)
            if not self.is_valid(link):
                continue
            if link in self.local_urls:
                # already in the set
                continue
            if base not in link:
                # external link
                if link not in self.external_urls:
                    self.external_urls.append(link)
                continue
            self.local_urls.append(link)
            if link not in self.new_urls and link not in self.processed_urls:
                self.new_urls.append(link)


def main():
    # url = "http://ya.ru"
    url = "http://konstds.ru"
    # url = "http://crawler-test.com/"
    # url = "https://yandex.ru"
    start = timeit.default_timer()
    crawler = Crawler(url)
    asyncio.run(crawler.run())
    local_urls = crawler.get_local()
    processing_time = timeit.default_timer() - start
    print(f"Processing time: {processing_time}\n")

    domain_name = f"{urlparse(url).netloc}_async"
    creating_sitemap(local_urls, domain_name, processing_time)
    pretty_print_xml(f"./ready_sitemaps/sitemap_{domain_name}.xml")


if __name__ == '__main__':
    main()
