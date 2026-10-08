import matplotlib.pyplot as plt
import networkx as nx


def bellman_ford(routing_table, neighbor_tables, cost_to_neighbors):
    updated_table = routing_table.copy()
    for neighbor_id, neighbor_table in neighbor_tables.items():
        link_cost = cost_to_neighbors[neighbor_id]
        for destination, cost in neighbor_table.items():
            new_cost = link_cost + cost
            if new_cost < updated_table[destination]:
                updated_table[destination] = new_cost
    return updated_table


def print_routing_table(routing_table):
    print("Destination\tCost")
    for destination, cost in routing_table.items():
        print(f"{destination}\t\t{cost}")


def simulate_rip(n, initial_tables, graph, iterations):
    routing_tables = initial_tables.copy()
    for iteration in range(iterations):
        print(f"\nIteration {iteration + 1}:")
        new_tables = []
        for i in range(n):
            current_table = routing_tables[i]
            neighbors = list(graph.neighbors(i))
            neighbor_tables = {j: routing_tables[j] for j in neighbors}
            cost_to_neighbors = {j: graph[i][j]["weight"] for j in neighbors}
            updated_table = bellman_ford(
                current_table, neighbor_tables, cost_to_neighbors
            )
            new_tables.append(updated_table)
            print(f"Router {i} Routing Table:")
            print_routing_table(updated_table)
            print()
        routing_tables = new_tables
    return routing_tables


def create_graph():
    G = nx.Graph()
    edges = [
        (0, 1, 1),
        (0, 2, 1),
        (1, 2, 1),
        (1, 3, 1),
        (2, 4, 1),
        (3, 4, 1),
        (3, 5, 1),
        (4, 5, 1),
        (0, 5, 1),
    ]
    G.add_weighted_edges_from(edges)
    return G


def init_tables(G, n):
    tables = []
    for i in range(n):
        table = {}
        for j in range(n):
            if i == j:
                table[j] = 0
            elif G.has_edge(i, j):
                table[j] = G[i][j]["weight"]
            else:
                table[j] = float("inf")
        tables.append(table)
    return tables


def draw_comparison(graph, initial_tables, final_tables, n):
    plt.figure(figsize=(14, 6))

    # 1. Initial Physical Network Topology
    pos = nx.circular_layout(graph)
    initial_labels = nx.get_edge_attributes(graph, "weight")

    plt.subplot(1, 2, 1)
    nx.draw(
        graph,
        pos,
        with_labels=True,
        node_color="lightcoral",
        node_size=800,
        font_size=10,
        font_weight="bold",
    )
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=initial_labels)
    plt.title("Initial Physical Network Topology")

    # 2. Final Converged Complete Graph (Virtual Reachability Graph)
    # Create a fully connected graph Kn
    final_graph = nx.complete_graph(n)

    # Assign converged shortest path distance from routing tables as edge weights
    final_labels = {}
    for u, v in final_graph.edges():
        dist = final_tables[u][v]
        final_graph[u][v]["weight"] = dist
        final_labels[(u, v)] = int(dist) if dist != float("inf") else "∞"

    plt.subplot(1, 2, 2)
    nx.draw(
        final_graph,
        pos,
        with_labels=True,
        node_color="lightgreen",
        node_size=800,
        font_size=10,
        font_weight="bold",
    )
    nx.draw_networkx_edge_labels(
        final_graph, pos, edge_labels=final_labels, label_pos=0.3
    )
    plt.title("Final State: Fully Connected Reachability Graph")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    n = 6
    iterations = 6
    graph = create_graph()
    initial_tables = init_tables(graph, n)

    print("Initial Routing Tables:")
    for idx, table in enumerate(initial_tables):
        print(f"Router {idx}: {table}")

    final_tables = simulate_rip(n, initial_tables, graph, iterations)

    print("Final Routing Tables:")
    for idx, table in enumerate(final_tables):
        print(f"Router {idx}: {table}")

    # Compare physical topology vs fully connected logical reachability graph
    draw_comparison(graph, initial_tables, final_tables, n)