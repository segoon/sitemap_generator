#!/usr/bin/env python
import asyncio
import sys
import timeit
from typing import Dict, List
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup
from generator.drawing_graph import draw
from generator.xml_creater import creating_sitemap, pretty_print_xml
from loguru import logger

logger.add(
    "debug_async.log",
    format="{time} {level} {message}",
    level="DEBUG",
    rotation="100KB",
    compression="zip",
)


class Crawler:
    def __init__(self, url: str = "") -> None:
        self.new_urls: List[str] = [url]
        self.processed_urls: List[str] = []
        self.local_urls: List[str] = [url]
        self.external_urls: List[str] = []
        self.broken_urls: List[str] = []
        self.graph: Dict[str, List[str]] = {}

    def get_processed(self) -> List[str]:
        return self.processed_urls

    def get_local(self) -> List[str]:
        return self.local_urls

    def get_external(self) -> List[str]:
        return self.external_urls

    def get_broken(self) -> List[str]:
        return self.broken_urls

    def get_graph(self) -> Dict[str, List[str]]:
        return self.graph

    def is_valid(self, url: str) -> bool:
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    async def get_responce(self, session: 'aiohttp.client.ClientSession', url: str) -> str:
        async with session.get(url) as response:
            return await response.text()

    async def run(self) -> None:
        async with aiohttp.ClientSession() as session:
            while self.new_urls:
                url = self.new_urls.pop(0)
                logger.info(f"Processing: {url}")
                try:
                    task = asyncio.create_task(self.crawl(session, url))
                    await task
                except Exception as err:
                    self.broken_urls.append(url)
                    logger.warning(f"Failed: {url}")
                    logger.error(f"Error: {err}")
                finally:
                    self.processed_urls.append(url)

    async def crawl(self, session: 'aiohttp.client.ClientSession', url: str) -> None:
        self.graph[url] = []
        url_parsed = urlparse(url)
        base = url_parsed.netloc
        root_scheme = url_parsed.scheme
        response = await self.get_responce(session, url)
        soup = BeautifulSoup(response, "lxml")
        for a_tag in soup.find_all("a"):
            link = a_tag.get("href")
            if link and link.startswith("/"):
                link = urljoin(url, link)
            if not self.is_valid(link):
                continue
            tmp_link = urlparse(link)
            link = tmp_link._replace(
                scheme=root_scheme,
                params='',
                query='',
                fragment='',
            ).geturl()
            if link in self.local_urls or link == url:
                # already in the set
                continue
            if base not in link:
                # external link
                if link not in self.external_urls:
                    self.external_urls.append(link)
                continue
            self.local_urls.append(link)
            self.graph[url].append(link)
            if link not in self.new_urls and link not in self.processed_urls:
                self.new_urls.append(link)


def main(args: List[str] = sys.argv):
    url = args[1]
    start = timeit.default_timer()
    crawler = Crawler(url)
    asyncio.run(crawler.run())
    local_urls = crawler.get_local()
    processing_time = timeit.default_timer() - start
    logger.info(f"Processing time: {processing_time}")
    local_urls_graph = crawler.get_graph()

    domain_name = f"{urlparse(url).netloc}_async"
    creating_sitemap(local_urls, domain_name, processing_time)
    pretty_print_xml(f"./ready_sitemaps/sitemap_{domain_name}.xml")

    draw(local_urls_graph, domain_name)


if __name__ == '__main__':
    main()
