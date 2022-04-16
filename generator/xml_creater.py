import xml.etree.cElementTree as ET
from lxml import etree
import datetime


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
    tree.write(f"./ready_sitemaps/sitemap_{domain_name}.xml",
               encoding='utf-8', xml_declaration=True)
    print("Sitemap ready in './ready_sitemaps'")


def pretty_print_xml(xml_file_path):
    assert xml_file_path is not None
    parser = etree.XMLParser(resolve_entities=False, strip_cdata=False)
    document = etree.parse(xml_file_path, parser)
    document.write(xml_file_path, pretty_print=True,
                   xml_declaration=True, encoding="utf-8")
