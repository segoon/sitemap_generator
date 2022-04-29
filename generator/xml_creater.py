"""XML creating module."""
import datetime
import xml.etree.cElementTree as Et

from loguru import logger
from lxml import etree


def creating_sitemap(urls, domain_name, processing_time):
    """
    Make xml sitemap file.

    Args:
        urls(list): local urls.
        domain_name(str): name of root url.
        processing_time(int): the time of the crawler operation
    """
    logger.info("Creating sitemap...")
    root = Et.Element("urlset")
    root.attrib['xmlns:xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
    root.attrib['xsi:schemaLocation'] = "http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd"
    root.attrib['xmlns'] = "http://www.sitemaps.org/schemas/sitemap/0.9"
    comment = Et.Comment(
        f"Processing time: {processing_time}, links found: {len(urls)}",
    )
    root.insert(0, comment)
    dt = datetime.datetime.now().strftime("%Y-%m-%d")
    for url in urls:
        doc = Et.SubElement(root, "url")
        Et.SubElement(doc, "loc").text = url
        Et.SubElement(doc, "lastmod").text = dt
        Et.SubElement(doc, "changefreq").text = "once"
        Et.SubElement(doc, "priority").text = "1.0"

    tree = Et.ElementTree(root)
    tree.write(
        f"./ready_sitemaps/sitemap_{domain_name}.xml",
        encoding='utf-8',
        xml_declaration=True,
    )
    logger.info("Sitemap ready in './ready_sitemaps'")


def pretty_print_xml(xml_file_path):
    """
    Make xml prettier.

    Args:
        xml_file_path(str): path to xml file.
    """
    parser = etree.XMLParser(resolve_entities=False, strip_cdata=False)
    document = etree.parse(xml_file_path, parser)
    document.write(
        xml_file_path,
        pretty_print=True,
        xml_declaration=True,
        encoding="utf-8",
    )
