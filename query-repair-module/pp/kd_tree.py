import pandas as pd
import heapq

class kd_tree:
    """
    KD-Tree where each node contains a cluster of data points, with accurate parent-child level relationships.
    """

    def __init__(self, points, dim, bucket_size=10, dist_sq_func=None):
        """Initialize the KD-Tree with dimensions and bucket size for clustering."""
        self._bucket_size = bucket_size
        self._dim = dim
        self._dist_sq_func = dist_sq_func or (lambda a, b: sum((x - b[i]) ** 2 for i, x in enumerate(a)))
        self._cluster_id = 1  # Initialize cluster ID starting from 1, reserve 0 for root
        self._root = self._make(points, 0, 0, None)  # Root node starts at level 0, cluster ID 0, no parent

    def __iter__(self):
        stack = [self._root]
        while stack:
            node = stack.pop()
            if node:
                if 'right' in node and node['right']:
                    stack.append(node['right'])
                if 'left' in node and node['left']:
                    stack.append(node['left'])
                if 'Data points' in node and 'Data points' in node['Data points'] and node['Data points']:
                    yield node['Data points']

    def _make(self, points, i, level, parent_id):
        """Recursively build the KD-Tree with proper parent ID and level tracking."""
        current_id = self._cluster_id
        self._cluster_id += 1  # Prepare ID for this node before creating children

        if len(points) <= self._bucket_size:               
            return {
                'left': None,
                'right': None,
                'Data points': points,
                'Level': level,
                'Cluster Id': current_id,
                'Parent Id': parent_id,
                'Parent level': level - 1 if parent_id is not None else None  # Track parent level

            }

        points.sort(key=lambda x: x[i])
        i = (i + 1) % self._dim
        m = len(points) // 2

        # Build left and right subtrees with the current node ID as their parent ID and the correct parent level
        left_child = self._make(points[:m], i, level + 1, current_id)
        right_child = self._make(points[m:], i, level + 1, current_id)

        return {
            'left': left_child,
            'right': right_child,
            'Data points': self._aggregate_points(left_child['Data points'], right_child['Data points']),
            'Level': level,
            'Cluster Id': current_id,
            'Parent Id': parent_id,
            'Parent level': level - 1  # Calculate parent level
        }

    def _aggregate_points(self, left_points, right_points):
        # Simply combine the lists of points
        return left_points + right_points

    def _flatten_tree(self, node):
        """Output tree structure for saving to CSV."""
        if not node:
            return []
        left_nodes = self._flatten_tree(node['left'])
        right_nodes = self._flatten_tree(node['right'])
        current_node = [{
            'Level': node['Level'],
            'Cluster Id': node['Cluster Id'],
            'Parent level': node['Parent level'] if node['Parent Id'] is not None else None,
            'Parent Id': node['Parent Id'],
            'Data points': node['Data points']
        }]
        return left_nodes + current_node + right_nodes

    def save_to_csv(self, filename):
        """Save the tree structure to a CSV file."""
        nodes = self._flatten_tree(self._root)
        df = pd.DataFrame(nodes, columns=['Level', 'Cluster Id', 'Parent level', 'Parent Id', 'Data points'])
        filename = filename.replace(" ", "_").replace(",", "_")
        df.to_csv(filename, index=False)
        print(f"KD-Tree saved to {filename}")

    def to_dict(self):
        """
        Convert the entire KD-Tree into a nested dictionary.
        This makes it easier to serialize, store, or manipulate the tree in applications.
        """
        def recurse(node, result):
            if not node:
                return None
                
            # Convert each node to a dictionary including its children
            result.append({
                'Level': node['Level'],
                'Cluster Id': node['Cluster Id'],
                'Parent cluster': node['Parent Id'],
                'Parent level': node['Parent level'],
                'Data points': node['Data points']
            })
             # Recurse through children without adding them as sub-dictionaries
            if node['left']:
                recurse(node['left'], result)
            if node['right']:
                recurse(node['right'], result)

        result = []
        recurse(self._root, result)
        return result
