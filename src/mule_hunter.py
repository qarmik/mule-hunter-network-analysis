import csv
import networkx as nx
from collections import defaultdict


def load_accounts(csv_path):
    """
    Load account records from CSV into a list of dicts.
    Each row represents one account.
    """
    records = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    return records


def build_account_graph(records):
    """
    Build an undirected graph where:
    - Each account_id is a node
    - An edge exists if two accounts share an attribute
    """
    G = nx.Graph()

    # Index accounts by attributes we care about
    device_index = defaultdict(list)
    ip_index = defaultdict(list)

    for r in records:
        account_id = r["account_id"]
        G.add_node(account_id)

        device_index[r["device_id"]].append(account_id)
        ip_index[r["ip_address"]].append(account_id)

    # Strong links: shared device
    for device, accounts in device_index.items():
        if len(accounts) > 1:
            for i in range(len(accounts)):
                for j in range(i + 1, len(accounts)):
                    G.add_edge(
                        accounts[i],
                        accounts[j],
                        reason="shared_device"
                    )

    # Weak links: shared IP
    for ip, accounts in ip_index.items():
        if len(accounts) > 1:
            for i in range(len(accounts)):
                for j in range(i + 1, len(accounts)):
                    # Do not overwrite a stronger link
                    if not G.has_edge(accounts[i], accounts[j]):
                        G.add_edge(
                            accounts[i],
                            accounts[j],
                            reason="shared_ip"
                        )

    return G


def analyse_clusters(G):
    """
    Identify connected components and print cluster summaries.
    """
    clusters = list(nx.connected_components(G))

    print(f"\nDetected {len(clusters)} clusters:\n")

    for idx, cluster in enumerate(clusters, start=1):
        print(f"Cluster {idx}:")
        print(f" Accounts: {', '.join(sorted(cluster))}")

        if len(cluster) == 1:
            print(" Interpretation: Isolated account\n")
            continue

        # Compute simple centrality
        subgraph = G.subgraph(cluster)
        centrality = nx.degree_centrality(subgraph)

        sorted_nodes = sorted(
            centrality.items(),
            key=lambda x: x[1],
            reverse=True
        )

        top_node, score = sorted_nodes[0]
        print(f" Possible coordinator candidate: {top_node}")
        print(" Interpretation: Review for organised control\n")


def main():
    csv_path = "data/sample_data.csv"
    records = load_accounts(csv_path)
    graph = build_account_graph(records)
    analyse_clusters(graph)

if __name__ == "__main__":
    main()

