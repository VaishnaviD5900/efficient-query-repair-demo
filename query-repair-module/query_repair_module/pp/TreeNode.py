class TreeNode:
    def __init__(self, level, cluster_id, data_points):
        self.level = level
        self.cluster_id = cluster_id
        self.data_points = data_points
        self.children = []