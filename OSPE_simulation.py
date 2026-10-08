import heapq
import matplotlib.pyplot as plt
import networkx as nx


# 1. Dijkstra's Algorithm implementation for Shortest Path Tree
def dijkstra_ospf(graph, source):
    """Computes the shortest paths and shortest path tree (SPT) from a source router

    using Dijkstra's algorithm based on OSPF link costs.
    """
    distances = {node: float("inf") for node in graph.nodes()}
    previous = {node: None for node in graph.nodes()}
    distances[source] = 0

    # Priority queue storing (cost, router_id)
    pq = [(0, source)]

    while pq:
        current_cost, u = heapq.heappop(pq)

        if current_cost > distances[u]:
            continue

        for v in graph.neighbors(u):
            weight = graph[u][v]["weight"]
            distance = current_cost + weight

            if distance < distances[v]:
                distances[v] = distance
                previous[v] = u
                heapq.heappush(pq, (distance, v))

    return distances, previous


# 2. Simulate Link-State Advertisements (LSAs) & LSDB Synchronization
def simulate_lsa_flooding(graph):
    """Simulates each router broadcasting its local links (LSAs)

    to ensure every router has an identical Link-State Database (LSDB).
    """
    lsdb = {}
    print("--- Simulating LSA Flooding & LSDB Synchronization ---")
    for node in graph.nodes():
        # LSA contains connected links and their weights
        local_lsa = {
            neighbor: graph[node][neighbor]["weight"]
            for neighbor in graph.neighbors(node)
        }
        lsdb[node] = local_lsa
        print(f"LSA from Router {node}: {local_lsa}")
    print("\nAll routers have synchronized their LSDB.\n")
    return lsdb


# 3. Print OSPF Routing Table and Shortest Path Tree
def print_ospf_tables(n, graph):
    all_spts = {}
    for source in range(n):
        distances, previous = dijkstra_ospf(graph, source)

        # Build Shortest Path Tree graph edges
        spt_edges = []
        for node, parent in previous.items():
            if parent is not None:
                spt_edges.append((parent, node, graph[parent][node]["weight"]))

        all_spts[source] = spt_edges

        print(f"--- Router {source} OSPF Routing Table ---")
        print("Destination\tNext Hop\tCost")
        for dest in range(n):
            if dest == source:
                print(f"{dest}\t\t-\t\t0")
                continue

            # Trace path back to find next hop
            curr = dest
            while previous[curr] != source and previous[curr] is not None:
                curr = previous[curr]
            next_hop = curr if previous[curr] is not None else "Unreachable"

            print(f"{dest}\t\t{next_hop}\t\t{distances[dest]}")
        print()

    return all_spts


# 4. Create Weighted Physical Topology
def create_ospf_graph():
    G = nx.Graph()
    # Edges defined as (u, v, cost/bandwidth metric)
    edges = [
        (0, 1, 2),
        (0, 2, 5),
        (1, 2, 1),
        (1, 3, 4),
        (2, 4, 2),
        (3, 4, 1),
        (3, 5, 3),
        (4, 5, 1),
        (0, 5, 7),
    ]
    G.add_weighted_edges_from(edges)
    return G


# 5. Visualizer comparing Network Topology vs. Shortest Path Tree (SPT)
def draw_ospf_comparison(graph, spt_edges, source_router):
    pos = nx.spring_layout(graph, seed=42)
    labels = nx.get_edge_attributes(graph, "weight")

    plt.figure(figsize=(14, 6))

    # Plot 1: Full Network Topology with Link Costs
    plt.subplot(1, 2, 1)
    nx.draw(
        graph,
        pos,
        with_labels=True,
        node_color="skyblue",
        node_size=800,
        font_size=10,
        font_weight="bold",
    )
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)
    plt.title("Full OSPF Network Topology (LSDB)")

    # Plot 2: Shortest Path Tree (SPT) for selected Router
    spt_graph = nx.Graph()
    spt_graph.add_nodes_from(graph.nodes())
    spt_graph.add_weighted_edges_from(spt_edges)
    spt_labels = nx.get_edge_attributes(spt_graph, "weight")

    plt.subplot(1, 2, 2)
    node_colors = [
        "gold" if node == source_router else "lightgreen"
        for node in spt_graph.nodes()
    ]
    nx.draw(
        spt_graph,
        pos,
        with_labels=True,
        node_color=node_colors,
        node_size=800,
        font_size=10,
        font_weight="bold",
    )
    nx.draw_networkx_edge_labels(spt_graph, pos, edge_labels=spt_labels)
    plt.title(f"Shortest Path Tree (SPT) for Router {source_router}")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    n = 6
    graph = create_ospf_graph()

    # Step 1: LSA Exchange & LSDB Sync
    simulate_lsa_flooding(graph)

    # Step 2: Dijkstra's Algorithm execution per router
    spts = print_ospf_tables(n, graph)

    # Step 3: Draw Network Topology vs. SPT for Router 0
    draw_ospf_comparison(graph, spts[0], source_router=0)