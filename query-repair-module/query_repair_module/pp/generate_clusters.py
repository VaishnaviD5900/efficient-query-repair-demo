from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial import ConvexHull
from .generate_convex_hull import generate_convex_hull
import pandas as pd

class generate_clusters:
    def generating_clusters(self, df_merged):
        # Perform hierarchical clustering      
        Z = linkage(df_merged, method='complete', metric='euclidean')
        all_clusters = self.get_clusters_at_each_level(Z, len(df_merged))

        return all_clusters

    # Function to get clusters and their data points at each hierarchical level
    def get_clusters_at_each_level(self, Z, num_data_points):
        all_clusters = {}
        for level in range(1, num_data_points):
            cluster_labels = fcluster(Z, level, criterion='maxclust')
            clusters = {}
            for i, label in enumerate(cluster_labels):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(i)

            all_clusters[level] = clusters      

        all_clusters[num_data_points] = {i+1: [i] for i in range(num_data_points)}

        return all_clusters

    def track_cluster_hierarchy(self, all_clusters):
        cluster_hierarchy = {}
        levels = sorted(all_clusters.keys())

        for level in levels:

            cluster_hierarchy[level] = {}
            for cluster_id, points in all_clusters[level].items():
                parent_clusters = set()
                for point in points:
                    if level-1 in all_clusters:
                        for parent_cluster_id, parent_points in all_clusters[level-1].items():
                            if point in parent_points:
                                parent_clusters.add(parent_cluster_id)

                # Select a single parent, the first one
                if parent_clusters:
                    parent_id = next(iter(parent_clusters))  # Take the first parent
                else:
                    parent_id = None  # Or some default value if no parent is found

                cluster_hierarchy[level][cluster_id] = parent_id

        return cluster_hierarchy
    
    def hierarchical_loop(self, df_merged):
        all_clusters = self.generating_clusters(df_merged)
        cluster_hierarchy = self.track_cluster_hierarchy(all_clusters)
        #convex_hull = generate_convex_hull()
        cluster_tree = []
        for level, clusters in cluster_hierarchy.items():
            for cluster_id, parent_cluster in clusters.items():
                points = all_clusters[level][cluster_id]
                cluster_data = [df_merged[i].tolist() for i in points]
                cluster_info = {
                    'Level': level,
                    'Cluster Id': cluster_id,
                    'Parent level': level-1, 
                    'Parent cluster': parent_cluster,
                    'Data points': cluster_data
                }
                cluster_tree.append(cluster_info)
            #convex_hull.draw_convex_hulls(cluster_level)
        updated_cluster_tree = self.remove_duplicates_and_update_parents(cluster_tree)

        df = pd.DataFrame(updated_cluster_tree)
        # Save to CSV
        df.to_csv('cluster_tree.csv', index=False)
        
        return updated_cluster_tree


    def remove_duplicates_and_update_parents(self, cluster_tree):
        unique_clusters = {}
        updated_cluster_tree = []
        parent_mapping = {}

        for cluster in cluster_tree:
            cluster_tuple = (tuple(sorted([tuple(point) for point in cluster['Data points']])), len(cluster['Data points']))
            if cluster_tuple not in unique_clusters:
                unique_clusters[cluster_tuple] = (cluster['Level'], cluster['Cluster Id'])
                updated_cluster_tree.append(cluster)
            else:
                first_level, first_id = unique_clusters[cluster_tuple]
                parent_mapping[(cluster['Level'], cluster['Cluster Id'])] = (first_level, first_id)

        for cluster in updated_cluster_tree:
            parent_key = (cluster['Parent level'], cluster['Parent cluster'])
            if parent_key in parent_mapping:
                cluster['Parent level'], cluster['Parent cluster'] = parent_mapping[parent_key]

        return updated_cluster_tree

