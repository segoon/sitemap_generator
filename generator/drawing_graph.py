import networkx as nx
import itertools
# import numpy.random as rnd
import matplotlib.pyplot as plt


def draw(local_urls, domain_name):
    print("Creating graph...")
    graph = nx.Graph()
    for key, value in local_urls.items():
        graph.add_node(key)
        # print(f"key = {key}, value = {value}")
        for child in value:
            # graph.add_node(child)
            graph.add_edge(key, child)
    nx.draw(graph,
            arrows=True,
            alpha=0.4,
            edge_color="r",
            font_size=2,
            node_size=0,
            with_labels=True)
    ax = plt.gca()
    ax.margins(0.20)
    plt.axis("off")
    plt.savefig(f"./ready_site_graph/graph_{domain_name}.png", dpi=500)
    print(f"{domain_name} graph ready in './ready_site_graph'")
