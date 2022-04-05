#!/usr/bin/env python
from bs4 import BeautifulSoup
import xml.etree.cElementTree as ET
from lxml import etree
import requests
import timeit
import datetime
from urllib.parse import urlparse, urljoin
from collections import deque


def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def crawl(url):
    new_urls = deque([url])
    processed_urls = set()
    local_urls = set()
    external_urls = set()
    broken_urls = set()
    # process urls one by one until we exhaust the queue
    while len(new_urls):
        # move next url from the queue to the set of processed urls
        url = new_urls.popleft()
        processed_urls.add(url)
        # get url's content
        print(f"Processing {url}")
        try:
            response = requests.get(url)
        except Exception:
            # add broken urls to it's own set, then continue
            broken_urls.add(url)
            print(f"Failed to crawl: {url}")
            continue
        # extract base url to resolve relative links
        parts = urlparse(url)
        base = parts.netloc
        # create a beutiful soup for the html document
        soup = BeautifulSoup(response.text, "lxml")
        # print(soup)
        for a_tag in soup.find_all('a'):
            link = a_tag.attrs.get("href")
            print(f"link = {link}")
            if link == "" or link is None:
                continue
            link = urljoin(url, link)
            parsed_link = urlparse(link)
            link = parsed_link.scheme + "://" + parsed_link.netloc + parsed_link.path
            if not is_valid(link):
                continue
            if link in local_urls:
                # already in the set
                continue
            if base not in link:
                # external link
                if link not in external_urls:
                    external_urls.add(link)
                continue
            local_urls.add(link)
            if link not in (new_urls, processed_urls):
                new_urls.append(link)
    return (processed_urls, local_urls, external_urls, broken_urls)


def creating_sitemap(urls, domain_name, processing_time):
    print('Creating sitemap...')
    root = ET.Element('urlset')
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
                   xml_declaration=True, encoding='utf-8')


def main():
    url = "http://konstds.ru"
    # url = "http://crawler-test.com/"
    # url = "https://yandex.ru"
    start = timeit.default_timer()
    processed_urls, local_urls, external_urls, broken_urls = crawl(url)
    processing_time = timeit.default_timer() - start
    print(f"Processing time: {processing_time}\n")
    # print(
    #     f"processed_urls {len(processed_urls)}:\n"
    #     f"processed_urls = {processed_urls}\n"
    #     f"local_urls {len(local_urls)}:\n"
    #     f"local_urls = {local_urls}:\n"
    #     f"external_urls {len(external_urls)}:\n"
    #     f"external_urls = {external_urls}\n"
    #     f"broken_urls {len(broken_urls):}\n"
    #     f"broken_urls = {broken_urls}\n")

    domain_name = urlparse(url).netloc

    creating_sitemap(local_urls, domain_name, processing_time)
    pretty_print_xml(f"./sitemaps/sitemap_{domain_name}.xml")


if __name__ == '__main__':
    main()
