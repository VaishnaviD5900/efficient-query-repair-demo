import pandas as pd
import heapq

class kd_tree1:
    def __init__(self, points, dim, bucket_size, branches, dist_sq_func=None):
        self._bucket_size = bucket_size
        self._dim = dim
        self._branches = branches  # Number of branches per node
        self._dist_sq_func = dist_sq_func or (lambda a, b: sum((x - b[i]) ** 2 for i, x in enumerate(a)))
        self._cluster_id = 1
        self._root = self._make(points, 0, 0, None)

    def __iter__(self):
        stack = [self._root]
        while stack:
            node = stack.pop()
            if node and 'children' in node:
                for child in node['children']:
                    stack.append(child)
                if 'Data points' in node:
                    yield node['Data points']

    def _make(self, points, i, level, parent_id):
        current_id = self._cluster_id
        self._cluster_id += 1  # Increment ID for this node before creating children

        if len(points) <= self._bucket_size:
            # If points are at or below the bucket size but more than one, split into individual data points
            children = []
            for point in points:
                child_id = self._cluster_id
                self._cluster_id += 1
                children.append({
                    'children': [],  # No further children since these are individual points
                    'Data points': [point],
                    'Level': level + 1,
                    'Cluster Id': child_id,
                    'Parent cluster': current_id,
                    'Parent level': level
                })
            return {
                'children': children,
                'Data points': points,
                'Level': level,
                'Cluster Id': current_id,
                'Parent cluster': parent_id,
                'Parent level': level - 1
            }

        # Normal branching case
        points.sort(key=lambda x: x[i % self._dim])
        chunks = []
        num_points = len(points)
        chunk_size = max(1, num_points // self._branches)  # Avoid zero division and ensure at least one point per chunk
        for j in range(self._branches):
            start = j * chunk_size
            end = start + chunk_size if j < self._branches - 1 else num_points
            chunk_points = points[start:end]
            if chunk_points:
                child = self._make(chunk_points, i + 1, level + 1, current_id)
                chunks.append(child)

        return {
            'children': chunks,
            'Data points': points,
            'Level': level,
            'Cluster Id': current_id,
            'Parent cluster': parent_id,
            'Parent level': level - 1
        }


    def _aggregate_points(self, left_child, right_child):
        # Combine data points from the left and right children
        aggregated = []
        if left_child and 'Data points' in left_child:
            aggregated.extend(left_child['Data points'])
        if right_child and 'Data points' in right_child:
            aggregated.extend(right_child['Data points'])
        return aggregated


    def _flatten_tree(self, node):
        if not node:
            return []
        result = [{
            'Level': node['Level'],
            'Cluster Id': node['Cluster Id'],
            'Parent level': node['Parent level'],
            'Parent Id': node['Parent cluster'],
            'Data points': node['Data points']
        }]
        if 'children' in node:
            for child in node['children']:
                result.extend(self._flatten_tree(child))
        return result

    def save_to_csv(self, filename):
        nodes = self._flatten_tree(self._root)
        df = pd.DataFrame(nodes, columns=['Level', 'Cluster Id', 'Parent level', 'Parent cluster', 'Data points'])
        filename = filename.replace(" ", "_").replace(",", "_")
        df.to_csv(filename, index=False)
        #print(f"KD-Tree saved to {filename}")

    def flatten_tree(self):
        def recurse(node):
            if not node:
                return []
            # Start with the current node
            flattened = [node]
            # If the node has children, extend the list with the results of the recursion
            if 'children' in node and node['children']:
                for child in node['children']:
                    flattened.extend(recurse(child))
            return flattened

        return recurse(self._root)


