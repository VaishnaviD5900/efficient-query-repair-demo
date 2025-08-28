import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial import ConvexHull
from scipy.spatial.qhull import QhullError
import matplotlib.pyplot as plt
import pandas as pd
from .Point import Point 

class generate_convex_hull:

    def Left_index(self, points):
        minn = 0
        for i in range(1,len(points)):
            if points[i].x < points[minn].x:
                minn = i
            elif points[i].x == points[minn].x:
                if points[i].y > points[minn].y:
                    minn = i
        return minn

    def orientation(self, p, q, r):
            val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
            if val == 0:
                return 0
            elif val > 0:
                return 1
            else:
                return 2

    def convexHull(self, points, n):
            if n < 3:
                return []
            l = self.Left_index(points)
            hull = []
            p = l
            q = 0
            while(True):
                hull.append(p)
                q = (p + 1) % n
                for i in range(n):
                    if(self.orientation(points[p], points[i], points[q]) == 2):
                        q = i
                p = q
                if(p == l):
                    break
            return [points[i] for i in hull]



    def calculate_convex_hulls_for_tree(self, cluster_tree):
        hulls = []
        for cluster in cluster_tree:
            predicates_points = np.array(cluster['Data points'])
            #constraint_points = np.array(cluster['Constraint points'])
            if len(predicates_points) < 7:
                
                hull_info = {
                    'Data points': predicates_points.tolist(),
                    'Level': cluster['Level'],
                    'Cluster Id': cluster['Cluster Id']
                    #'Constraint Points': hull_constraint_points
                }
                hulls.append(hull_info)
                
                continue
            try:
                hull = ConvexHull(predicates_points)
                hull_points = predicates_points[hull.vertices].tolist()
                #hull_constraint_points = constraint_points[hull.vertices].tolist()
                hull_points.sort()
                hull_info = {
                    'Data points': hull_points,
                    'Level': cluster['Level'],
                    'Cluster Id': cluster['Cluster Id']
                    #'Constraint Points': hull_constraint_points
                }
                hulls.append(hull_info)
            except Exception as e:
                print(f"Could not compute convex hull for cluster {cluster['Cluster Id']} at level {cluster['Level']}: {e}")

                continue
        return hulls

    def draw_convex_hulls(self, cluster_tree):
        plt.figure(figsize=(10, 6))
        colors = ['blue', 'red', 'green', 'yellow', 'purple', 'orange', 'cyan', 'magenta']

        for idx, cluster in enumerate(cluster_tree):
            points = np.array(cluster['Data points'])
            if len(points) < 3 or len(np.unique(points, axis=0)) < 3:
                continue  # Skip clusters that can't form a convex hull
            try:
                hull = ConvexHull(points)
            except QhullError:
                continue  # Skip clusters that cause Qhull errors
            color = colors[idx % len(colors)]

            # Plot cluster points
            plt.scatter(points[:, 0], points[:, 1], label=f'Level {cluster["Level"]}, Cluster {cluster["Cluster Id"]}',color=color)

            # Plot convex hull
            for simplex in hull.simplices:
                plt.plot(points[simplex, 0], points[simplex, 1], color)

            # Fill convex hull
            plt.fill(points[hull.vertices, 0], points[hull.vertices, 1], color, alpha=0.3)

        plt.xlabel('Income')
        plt.ylabel('Num of Children')
        plt.legend()
        plt.title('Convex Hulls for Each Cluster')
        plt.show()
