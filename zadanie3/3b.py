import numpy as np
import matplotlib.pyplot as plt
import time
import random


def generate_points(seed):
    # Generate 20 random points
    np.random.seed(seed)
    points = np.random.uniform(low=-5000, high=5000, size=(20, 2))

    # Generate additional 40000 points
    for _ in range(40000):
        random_point = points[np.random.randint(0, len(points))]
        x_offset, y_offset = np.random.uniform(low=-100, high=100, size=2)
        new_point = random_point + [x_offset, y_offset]
        points = np.vstack([points, new_point])

    return points


def euclidean_distance(p1, p2):
    return np.sqrt(np.sum((p1 - p2) ** 2, axis=1))


# Find the closest centroid for each point
# Save the old centroids
# Update the centroids
# Check for convergence
def k_means_centroid(points, k, max_iter):
    global labels
    # Initialize random k centroids
    centroids = np.random.uniform(np.amin(points, axis=0), np.amax(points, axis=0), size=(k, points.shape[1]))

    # Repeat until convergence
    for _ in range(max_iter):

        # Find the closest centroid
        labels = []
        for point in points:
            # calculate the distance between the point and each centroid
            distances = euclidean_distance(point, centroids)
            # assign the point to the closest centroid
            label = np.argmin(distances)
            # add the label for the point to the list of labels
            labels.append(label)

        # convert the list of labels to a numpy array
        labels = np.array(labels)

        # reposition centroids
        cluster_points = []
        for i in range(k):
            # find the points that belong to the cluster
            cluster_points.append(np.argwhere(labels == i))

        # calculate the new centroids
        cluster_centers = []
        for i, indices in enumerate(cluster_points):
            if len(indices) == 0:
                # if there are no points in the cluster, keep the old centroid
                cluster_centers.append(centroids[i])
            else:
                # calculate the new centroid as the mean of the points in the cluster and append it to the list
                cluster_centers.append(np.mean(points[indices], axis=0)[0])

        # if the difference between the old and new centroids is small enough
        # then we have converged
        if np.max(centroids - np.array(cluster_centers)) < 0.0001:
            break
        else:
            centroids = np.array(cluster_centers)

    return labels, centroids


def manhattan_distance(p1, p2):
    return np.abs((p1[0]-p2[0])) + np.abs((p1[1]-p2[1]))


def get_cost(points, medoids):
    clusters = {i:[] for i in range(len(medoids))}
    cst = 0
    for d in points:
        dst = np.array([manhattan_distance(d, md) for md in medoids])
        c = dst.argmin()
        clusters[c].append(d)
        cst+=dst.min()

    clusters = {k:np.array(v) for k,v in clusters.items()}
    return clusters, cst


# noinspection DuplicatedCode
def k_means_medoid(points, k, max_iter):
    medoids = np.array([points[i] for i in range(k)])

    random_number = random.randint(0, len(points))
    samples = np.array([points[(i * random_number) % len(points)] for i in range(20)])

    clusters, cost = get_cost(points, medoids)

    count = 0

    colors = np.array(np.random.randint(0, 255, size=(k, 4))) / 255
    colors[:, 3] = 1

    print("-----CLOSE THE PLOT TO CONTINUE-----")

    plt.title(f"Initial clusters")
    [plt.scatter(clusters[t][:, 0], clusters[t][:, 1], color=colors[t]) for t in range(k)]
    plt.scatter(medoids[:, 0], medoids[:, 1], facecolors='none', marker='o', s=100, edgecolors='black')
    plt.show()

    while True:
        swap = False
        print("Debug: iteration", count)
        for i in range(len(samples)):
            print("Debug: i", i)
            if not i in medoids:
                for j in range(k):
                    print("Debug: j", j)
                    tmp_meds = medoids.copy()
                    tmp_meds[j] = points[i]
                    clusters_, cost_ = get_cost(points, tmp_meds)

                    if cost_ < cost:
                        medoids = tmp_meds
                        cost = cost_
                        swap = True
                        clusters = clusters_
                        print(f"Medoids Changed to: {medoids}.")
        count += 1

        if count >= max_iter:
            print("End of the iterations.")
            break
        if not swap:
            print("No changes.")
            break

    return clusters, medoids


def average_distance_from_point_to_points(points, centroid):
    if len(points) == 0:
        return 0
    distances = euclidean_distance(points, centroid)
    return np.mean(distances)


# def k_means_centroid_recursive(points, max_iter, centroid):
#
#     if average_distance_from_point_to_points(points, centroid) < 500:
#         print("Debug: Mensi ako 500")
#         return np.array([]), np.array([])
#
#     labelz, centroids = k_means_centroid(points, 2, max_iter)
#     print("Centroids recursive", centroids)
#
#     cluster_points1 = getPointsInCluster(points, labelz, 0)
#     cluster_points2 = getPointsInCluster(points, labelz, 1)
#
#     # Find the average cluster size from the centroid if it is more than 500 then you
#     # divide and this is done in the loop until all clusters have that average less than 500
#
#     labelz1, centroids1 = k_means_centroid_recursive(cluster_points1, max_iter, centroids[0])
#     print("Debug: Centroids1", centroids1)
#     labelz2, centroids2 = k_means_centroid_recursive(cluster_points2, max_iter, centroids[1])
#     print("Debug: Centroids2", centroids2)
#
#     if labelz1.shape != labelz2.shape:
#         print("Not equal")
#         return labelz, centroids
#
#     if labelz1.size > 0 and labelz2.size > 0:
#         label_out = labelz1 + labelz2
#         centroid_out = centroids1 + centroids2
#     else:
#         label_out = labelz
#         centroid_out = centroids
#
#     return label_out, centroid_out


def getPointsInCluster(points, labelx, cluster_id):
    cluster_points = []
    for i, label in enumerate(labelx):
        if label == cluster_id:
            cluster_points.append(points[i])

    cluster_points = np.array(cluster_points)
    return cluster_points


# basically modify k_means_centroid and run it recursively
# def divisive_clustering_centroid(points, k, max_iter):
#     labels_here, centroids = k_means_centroid(points, k, max_iter)
#
#     label_buffer = []
#     centroid_buffer = []
#
#     label_buffer = np.array(label_buffer)
#     centroid_buffer = np.array(centroid_buffer)
#
#     cluster_points = []
#     for i in range(len(centroids)):
#         cluster_points.append(getPointsInCluster(points, labels_here, i))
#         labels_here1, centroids1 = k_means_centroid_recursive(cluster_points[i], max_iter, centroids[i])
#
#         print("Debug: Centroids1", centroids1)
#         print("Debug: Labels1", labels_here1)
#
#         label_buffer += labels_here1
#         centroid_buffer += centroids1
#
#     return label_buffer, centroid_buffer


# Evaluate the success/error rate of your cluster.
# We consider a successful clusterer to be one in which no cluster
# has an average distance of points from the center greater than 500.
def evaluate_clustering(choice, points, oids, labels_here, k):
    if choice == "centroid":
        for i in range(k):
            cluster_points = getPointsInCluster(points, labels_here, i)
            if cluster_points.size == 0:
                continue
            if average_distance_from_point_to_points(cluster_points, oids[i]) > 500:
                return False
        return True
    elif choice == "medoid":
        cluster_points, _ = get_cost(points, oids)
        for i in range(k):
            if cluster_points[i].size == 0:
                continue
            if average_distance_from_point_to_points(cluster_points[i], oids[i]) > 500:
                return False
        return True
    else:
        print("Invalid choice")
        print("Returning False")
        return False


def main():
    while True:
        seed = int(input("Enter seed (random number 0-100): "))
        k = int(input("Enter k (recommended <=20): "))
        points = generate_points(seed)
        iterations = int(input("Enter max iterations (recommended 100 for centroid, 1 for medoid): "))

        choice_main = int(input("Enter choice (1 - k-means centroid, 2 - k-means medoid, 3 - divisive clustering centroid): "))

        if choice_main == 1:
            # K-means
                print("Clustering with k-means centroid:")
                start = time.time()
                labels_main, centroids = k_means_centroid(points, k, iterations)
                end = time.time()
                print(f"Time taken: {end - start} seconds")
                print("Evaluate clustering:")
                if evaluate_clustering("centroid", points, centroids, labels_main, k):
                    print("Clustering successful")
                else:
                    print("Clustering unsuccessful")

                print("-----CLOSE THE PLOT TO CONTINUE-----")

                plt.scatter(points[:, 0], points[:, 1], c=labels_main)
                plt.scatter(centroids[:, 0], centroids[:, 1], facecolors='none', marker='o', s=100, edgecolors='black')
                plt.title("K-means centroid")
                plt.show()
            # End K-means
        elif choice_main == 2:
            # K-means medoid
                print("Clustering with k-means medoid:")
                start = time.time()
                # take only 50 points for testing
                # points = points[:50]
                clusters, medoids = k_means_medoid(points, k, iterations)
                end = time.time()
                print(f"Time taken: {end - start} seconds")
                print("Evaluate clustering:")
                if evaluate_clustering("medoid", points, medoids, clusters, k):
                    print("Clustering successful")
                else:
                    print("Clustering unsuccessful")
                colors = np.array(np.random.randint(0, 255, size=(k, 4))) / 255
                colors[:, 3] = 1

                print("-----CLOSE THE PLOT TO CONTINUE-----")

                plt.title(f"Final clusters - K-means medoid")
                [plt.scatter(clusters[t][:, 0], clusters[t][:, 1], color=colors[t]) for t in range(k)]
                plt.scatter(medoids[:, 0], medoids[:, 1], facecolors='none', marker='o', s=100, edgecolors='black')
                plt.show()
            # End K-means medoid
        elif choice_main == 3:
            print("Not implemented")
            # Divisive
            #     print("Clustering with divisive clustering centroid:")
            #     start = time.time()
            #     labels_buffer, centroids_buffer = divisive_clustering_centroid(points, k, iterations)
            #     end = time.time()
            #     print(f"Time taken: {end - start} seconds")
            #     plt.scatter(points[:, 0], points[:, 1], c=labels_buffer)
            #
            #     print("Debug: Labels buffer", labels_buffer)
            #     print("Debug: Centroid buffer", centroids_buffer)
            #
            #     plt.scatter(centroids_buffer[:, 0], centroids_buffer[:, 1], facecolors='none', marker='o', s=100, edgecolors='black')
            #     plt.title("Divisive clustering centroid")
            #     plt.show()
            # End Divisive
        elif choice_main == 4:
            print("Exiting...")
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()
