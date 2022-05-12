"""Drawing module."""
from typing import List

import networkx as nx
from loguru import logger
from matplotlib import pyplot as plt


def draw(local_urls: List[str], domain_name: str) -> None:
    """
    Get local_urls and draw links between pages.

    Args:
        local_urls(dict): diction with pages and links in it.
        domain_name(str): name of root url.
    """
    logger.info("Creating graph...")
    graph = nx.Graph()
    for url, links in local_urls.items():
        graph.add_node(url)
        for child in links:
            graph.add_node(child)
            graph.add_edge(url, child)
    nx.draw(
        graph,
        arrows=True,
        alpha=0.4,
        edge_color="r",
        font_size=2,
        node_size=0,
        with_labels=True,
    )
    ax = plt.gca()
    ax.margins(0.2)
    plt.axis("off")
    plt.savefig(f"./ready_site_graph/graph_{domain_name}.png", dpi=500)
    logger.info(f"{domain_name} graph ready in './ready_site_graph\n'")
