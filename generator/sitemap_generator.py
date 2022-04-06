#!/usr/bin/env python
from bs4 import BeautifulSoup
import xml.etree.cElementTree as ET
from lxml import etree
import requests
import timeit
import datetime
from urllib.parse import urlparse, urljoin


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

    def run(self):
        while self.new_urls:
            url = self.new_urls.pop(0)
            print(f"Processing: {url}")
            try:
                self.crawl(url)
            except Exception:
                self.broken_urls.append(url)
                print(f"Failed: {url}")
            finally:
                self.processed_urls.append(url)

    def crawl(self, url):
        base = urlparse(url).netloc
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "lxml")
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


def creating_sitemap(urls, domain_name, processing_time):
    print("Creating sitemap...")
    root = ET.Element("urlset")
    root.attrib['xmlns:xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
    root.attrib['xsi:schemaLocation'] = "http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd"
    root.attrib['xmlns'] = "http://www.sitemaps.org/schemas/sitemap/0.9"
    comment = ET.Comment(f"Processing time: {processing_time}, "
                         f"links found: {len(urls)}")
    root.insert(0, comment)
    dt = datetime.datetime.now().strftime("%Y-%m-%d")
    for url in urls:
        doc = ET.SubElement(root, "url")
        ET.SubElement(doc, "loc").text = url
        ET.SubElement(doc, "lastmod").text = dt
        ET.SubElement(doc, "changefreq").text = "once"
        ET.SubElement(doc, "priority").text = "1.0"

    tree = ET.ElementTree(root)
    tree.write(f"./sitemaps/sitemap_{domain_name}.xml",
               encoding='utf-8', xml_declaration=True)
    print("Sitemap ready in './sitemaps'")


def pretty_print_xml(xml_file_path):
    assert xml_file_path is not None
    parser = etree.XMLParser(resolve_entities=False, strip_cdata=False)
    document = etree.parse(xml_file_path, parser)
    document.write(xml_file_path, pretty_print=True,
                   xml_declaration=True, encoding="utf-8")


def main():
    url = "http://ya.ru"
    # url = "http://crawler-test.com/"
    # url = "https://yandex.ru"
    start = timeit.default_timer()
    crawler = Crawler(url)
    crawler.run()
    local_urls = crawler.get_local()
    processing_time = timeit.default_timer() - start
    print(f"Processing time: {processing_time}\n")

    domain_name = urlparse(url).netloc
    creating_sitemap(local_urls, domain_name, processing_time)
    pretty_print_xml(f"./sitemaps/sitemap_{domain_name}.xml")


if __name__ == '__main__':
    main()
