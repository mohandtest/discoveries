"""Small-network observables with definitions that permit disconnected graphs."""
from network_null import triangle_count


def measure(adj, reference):
    n = len(adj)
    unseen = set(range(n))
    components = 0
    while unseen:
        components += 1
        todo = [unseen.pop()]
        while todo:
            new = adj[todo.pop()] & unseen
            unseen.difference_update(new)
            todo.extend(new)
    squares = 0
    for u in range(n):
        for v in range(u+1, n):
            common = len(adj[u] & adj[v])
            squares += common * (common-1) // 2
    return dict(triangles=triangle_count(adj), four_cycles=squares//2,
                components=components,
                edge_overlap=sum(v in adj[u] for u, v in reference),
                degree_product=sum(len(adj[u])*len(adj[v]) for u in range(n) for v in adj[u] if u < v))
