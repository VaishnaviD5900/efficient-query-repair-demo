from collections import defaultdict

class parent_child_map:

    def precompute_all_descendants(self, cluster_tree):
        descendants = {}
        parent_child_map = defaultdict(list)
        
        # Use a stack to iterate over the tree structure without recursion
        for row in cluster_tree:
            parent_key = (row['Parent level'], row['Parent cluster'])
            child_key = (row['Level'], row['Cluster Id'])
            parent_child_map[parent_key].append(child_key) 


        for key in parent_child_map.keys():
            stack = [key]
            all_descendants = set()

            while stack:
                current = stack.pop()
                if current in parent_child_map:
                    children = parent_child_map[current]
                    all_descendants.update(children)
                    stack.extend(children)
            
            descendants[key] = all_descendants

        return descendants