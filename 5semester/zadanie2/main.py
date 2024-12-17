from typing import Type
import numpy as np
import matplotlib.pyplot as plt
import time
import point
from copy import copy
import colorsys
import datetime

#  --------------- GENERAL INFO ---------------
# 2D space; x, y coordinates in <-5000, 5000>
# function use camelCase
# variables use snake_case
#  l_ prefix for local variables
#  g_ prefix for global variables
#  c_ prefix for constants
#  m_ prefix for class member variables
#  --------------------------------------------
#  ------------- GLOBAL CONSTANTS / VARIABLES -------------
G_DEBUG = False  # turn on/off debug mode
G_MAX_POINTS = 40020  # number of points to generate
G_MILION = 1000000  # nanoseconds to milliseconds conversion
G_SUCCESSFUL_DISTANCE = 500  # mean of the distances from the middle point from single cluster
G_CLOSE_MIDDLE_POINT_DISTANCE_CENTROID = 100000  # squared euclidean distance between centroids, treshold for close points defined by me
G_CLOSE_MIDDLE_POINT_DISTANCE_MEDOID = 500  # manhattan distance between medoids, treshold for close points defined by me
G_MEDOIDS_NOT_CHANGED_LIMIT = 30  # if the medoids do not change for this number of iterations, stop the clustering
g_centroids_buffer: list[point.Point] = []  # middle points buffer for divisive clustering
g_cluster_number_counter = 0  # global counter for unique cluster numbers (Divisive clustering)
#  --------------------------------------------------------


# using seed to have reproducible results
def generatePoints(seed: int) -> list[point.Point]:
    np.random.seed(seed)

    points: list[point.Point]
    points = []

    vertices_set: set = set()
    
    # first vertex to initialize the array
    # size 2 means 2D so it is point with 2 coordinates (x, y)
    first_vertex = tuple(np.random.randint(low=-5000, high=5000 + 1, size=2, dtype=int))
    vertices_set.add(first_vertex)
    vertices = [first_vertex]

    # make these 20 vertices unique
    while len(vertices) < 20:
        vertex = tuple(np.random.randint(low=-5000, high=5000 + 1, size=2, dtype=int))
        if vertex in vertices_set:
            continue
        vertices_set.add(vertex)
        vertices.append(vertex)

    # generate additional 40000 points
    while len(vertices) < G_MAX_POINTS:
        # get random vertex
        random_vertex = vertices[np.random.randint(0, len(vertices))]
        # get random offset
        x_offset, y_offset = np.random.randint(low=-100, high=100 + 1, size=2, dtype=int)
        # create new vertex with random offset
        new_vertex = (random_vertex[0] + x_offset, random_vertex[1] + y_offset)

        # skip points out of bounds
        if new_vertex[0] < -5000 or new_vertex[0] > 5000 or new_vertex[1] < -5000 or new_vertex[1] > 5000:
            continue
        
        # skip duplicates
        if new_vertex in vertices_set:
            if G_DEBUG:
                print("Duplicate point (in 40000):", new_vertex)
            continue

        # concatenate new vertex to the array
        vertices_set.add(new_vertex)
        vertices.append(new_vertex)

    # create points from vertices
    for vertex in vertices:
        points.append(point.Point(np.array(vertex), None, None))

    return points


# e2 - Euclidean distance squared, return_type is always int
# e - Euclidean distance
# m - manhattan distance, return_type is always int
# Euclidean distance should stay squared, src: wikipedia k-means clustering
def distance(p1: np.ndarray, p2: np.ndarray, distance_type: str = 'e', return_type: Type[int | float] = int) -> int | float | None:
    dist: int | float | None = None

    if distance_type == 'e':
        if return_type == int:
            dist = int(np.sqrt(np.sum((p1 - p2) ** 2)))
        elif return_type == float:
            dist = np.sqrt(np.sum((p1 - p2) ** 2))
        else:
            print("distance: Invalid return_type")
    elif distance_type == 'e2':
        dist = np.sum((p1 - p2) ** 2)
    elif distance_type == 'm':
        dist = np.sum(np.abs(p1 - p2))
    else:
        print("distance: Invalid distance_type")

    return dist


def kMeansCentroid(l_points: list[point.Point], k: int, iterations: int, seed_to_print: int) -> list[point.Point]:

    centroids: list[point.Point]
    centroids = []
    
    # pick randomly k-points as centroids (but just their coordinates, not the whole point because centroids are not points)
    # and use them as initial centroids for the clusters
    # init centroids
    while len(centroids) < k:
        random_point = copy(l_points[np.random.randint(0, len(l_points))])
        # check for duplicates
        if random_point in centroids:
            continue
        
        # check for close points
        # if the distance between the random point (future centroid) and any of the centroids is less than NUMBER, do not add the point and generate new centroid
        is_okay = True
        for centroid in centroids:
            dist = distance(random_point.m_coordinates, centroid.m_coordinates, 'e2')
            
            if dist < G_CLOSE_MIDDLE_POINT_DISTANCE_CENTROID:
                is_okay = False
                break
                
        if is_okay:
            centroids.append(random_point)
        
    # assign cluster number to each centroid
    for i in range(0, k):
        centroids[i].m_cluster_number = i
        
    # plot init points with init centroids
    plotPoints(l_points, centroids, k, iterations, False, [], True, seed_to_print, "centroid")
    
    if G_DEBUG:
        print("Init centroids:")
        for c in centroids:
            print(c.m_coordinates)

    old_centroids: list[point.Point]
    
    # classify points to the nearest centroid
    for i in range(0, iterations):
        
        print("Iteration: ", i)
        
        # assign each point to the nearest centroid
        for l_point in l_points:
            min_distance = np.inf
            # for each point find the nearest centroid
            for centroid in centroids:
                dist = distance(l_point.m_coordinates, centroid.m_coordinates, 'e', int)
                if dist < min_distance:
                    min_distance = dist
                    l_point.m_cluster_number = centroid.m_cluster_number
                    l_point.m_distance_from_middle = min_distance

        # copy old centroids but not just references!
        old_centroids = []
        for centroid in centroids:
            old_centroids.append(copy(centroid))

        # update centroids
        for centroid in centroids:
            cluster_points = getPointsInOneCluster(l_points, centroid.m_cluster_number)
            new_centroid = np.mean([l_point.m_coordinates for l_point in cluster_points], axis=0, dtype=int)
            centroid.m_coordinates = new_centroid
            if G_DEBUG:
                print("new_centroid: ", new_centroid)
            
                for x in range(len(centroids)):
                    print("old_centroids: ", old_centroids[x].m_coordinates, ", centroids: ", centroids[x].m_coordinates)
            
        # check if the middle points changed
        if i > 0:
            if not middlePointsChanged(old_centroids, centroids):
                print("Centroids did not change, stopping the clustering, iteration:", i)
                global g_iteration_counter
                g_iteration_counter = i + 1  # because the iteration starts from 0
                if G_DEBUG:
                    for y in range(len(centroids)):
                        print("old_centroids: ", old_centroids[y].m_coordinates, ", centroids: ", centroids[y].m_coordinates)
                break
            
    return centroids


def kMeansMedoidPseudo(l_points: list[point.Point], k: int, iterations: int, seed_to_print: int) -> list[point.Point]:
    medoids: list[point.Point] = []
    
    # init medoids
    while len(medoids) < k:
        rand_num: int = np.random.randint(0, len(l_points))
        random_point = copy(l_points[rand_num])
        
        # check for duplicates
        if random_point in medoids:
            continue
        
        # check for close points
        # if the distance between the random point (future medoid) and any of the medoids is less than NUMBER, do not add the point and generate new medoid
        is_okay = True
        for medoid in medoids:
            dist = distance(random_point.m_coordinates, medoid.m_coordinates, 'm')
            
            if dist < G_CLOSE_MIDDLE_POINT_DISTANCE_MEDOID:
                is_okay = False
                break
                
        if is_okay:
            medoids.append(random_point)
        
    # assign cluster number to each medoid
    for i in range(0, k):
        medoids[i].m_cluster_number = i
        
    # plot init points with init medoids
    plotPoints(l_points, medoids, k, iterations, False, [], True, seed_to_print, "medoid_optimized_pseudo")
    
    if G_DEBUG:
        print("Init medoids:")
        for m in medoids:
            print(m.m_coordinates)

    # classify points to the nearest medoid
    old_medoids: list[point.Point]
    
    for i in range(0, iterations):
        
        print("Iteration: ", i)
        
        # assign each point to the nearest medoid
        for l_point in l_points:
            min_distance = np.inf
            # for each point find the nearest medoid
            for medoid in medoids:
                dist = distance(l_point.m_coordinates, medoid.m_coordinates, 'm', int)
                if dist < min_distance:
                    min_distance = dist
                    l_point.m_cluster_number = medoid.m_cluster_number
                    l_point.m_distance_from_middle = min_distance

        # copy old medoids but not just references!
        old_medoids = []
        for medoid in medoids:
            old_medoids.append(copy(medoid))

        # update medoids
        for medoid in medoids:
            cluster_points = [l_point for l_point in l_points if l_point.m_cluster_number == medoid.m_cluster_number]
            new_medoid = np.mean([l_point.m_coordinates for l_point in cluster_points], axis=0, dtype=int)
            
            # find the closest point to the new medoid coordinates (which is the mean of the cluster points)
            closest_point: point.Point = cluster_points[0]
            min_distance = np.inf
            for l_point in cluster_points:
                dist = distance(l_point.m_coordinates, new_medoid, 'm', int)
                if dist < min_distance:
                    min_distance = dist
                    closest_point = l_point
                    
            medoid.m_coordinates = closest_point.m_coordinates
            
            if G_DEBUG:
                print("new_medoid: ", closest_point.m_coordinates)
            
                for x in range(len(medoids)):
                    print("old_medoids: ", old_medoids[x].m_coordinates, ", medoids: ", medoids[x].m_coordinates)
            
        # check if the middle points changed
        if i > 0:
            if not middlePointsChanged(old_medoids, medoids):
                print("Medoids did not change, stopping the clustering, iteration:", i)
                global g_iteration_counter
                g_iteration_counter = i + 1  # because the iteration starts from 0
                if G_DEBUG:
                    for y in range(len(medoids)):
                        print("old_medoids: ", old_medoids[y].m_coordinates, ", medoids: ", medoids[y].m_coordinates)
                break
            
    return medoids


# REAL MEDOID IMPLEMENTATION !
def kMeansMedoidReal(l_points: list[point.Point], k: int, iterations: int, seed_to_print: int) -> list[point.Point]:
    medoids: list[point.Point] = []
    
    # init medoids
    while len(medoids) < k:
        rand_num: int = np.random.randint(0, len(l_points))
        random_point = copy(l_points[rand_num])
        
        # check for duplicates
        if random_point in medoids:
            continue
        
        # check for close points
        # if the distance between the random point (future medoid) and any of the medoids is less than NUMBER, do not add the point and generate new medoid
        is_okay = True
        for medoid in medoids:
            dist = distance(random_point.m_coordinates, medoid.m_coordinates, 'm')
            
            if dist < G_CLOSE_MIDDLE_POINT_DISTANCE_MEDOID:
                is_okay = False
                break
                
        if is_okay:
            medoids.append(random_point)
        
    # assign cluster number to each medoid
    for i in range(0, k):
        medoids[i].m_cluster_number = i
        
    # plot init points with init medoids
    plotPoints(l_points, medoids, k, iterations, False, [], True, seed_to_print, "medoid_real_implementation")
    
    if G_DEBUG:
        print("Init medoids:")
        for m in medoids:
            print(m.m_coordinates)

    # classify points to the nearest medoid and recalculate medoids (main loop of the function)
    old_medoids: list[point.Point] = []
    times_not_changed: int = 0
    
    for i in range(0, iterations):
        
        print("Iteration: ", i)
        global g_iteration_counter
        g_iteration_counter = i + 1
        
        # assign each point to the nearest medoid
        for l_point in l_points:
            min_distance = np.inf
            # for each point find the nearest medoid
            for medoid in medoids:
                dist = distance(l_point.m_coordinates, medoid.m_coordinates, 'm', int)
                if dist < min_distance:
                    min_distance = dist
                    l_point.m_cluster_number = medoid.m_cluster_number
                    l_point.m_distance_from_middle = min_distance


        # copy old medoids but not just references!
        old_medoids = copy(medoids)
        
        # calculate cost from all clusters for old medoids
        cost_from_all_clusters_old: int = getTotalCost(old_medoids, l_points)
        
        # update medoids
        new_medoid: point.Point = None
        
        while True:
            rand_number: int = np.random.randint(0, len(l_points))
            if G_DEBUG:
                print("rand_number: ", rand_number)
            new_medoid = copy(l_points[rand_number])
            
            # check for duplicates
            if new_medoid in medoids:
                continue
            
            is_okay = True
            for m in medoids:
                dist = distance(new_medoid.m_coordinates, m.m_coordinates, 'm')
                
                if dist < G_CLOSE_MIDDLE_POINT_DISTANCE_MEDOID:
                    is_okay = False
                    break
                
            if is_okay:
                break
            
        # replace random medoid with new one
        random_choice = np.random.randint(0, len(medoids))
        
        if G_DEBUG:
            print("random_choice (for medoid swap): ", random_choice)
            print(f"Swaping point: {medoids[random_choice].m_coordinates}, with {new_medoid.m_coordinates}")
            
        new_medoid.m_cluster_number = medoids[random_choice].m_cluster_number
        medoids[random_choice] = new_medoid

        # classify points to the nearest medoid for new medoids before calculating the cost
        # assign each point to the nearest medoid
        for l_point in l_points:
            min_distance = np.inf
            # for each point find the nearest medoid
            for medoid in medoids:
                dist = distance(l_point.m_coordinates, medoid.m_coordinates, 'm', int)
                if dist < min_distance:
                    min_distance = dist
                    l_point.m_cluster_number = medoid.m_cluster_number
                    l_point.m_distance_from_middle = min_distance
        
        cost_from_all_clusters_new: int = getTotalCost(medoids, l_points)
        
        if cost_from_all_clusters_new > cost_from_all_clusters_old:
            if G_DEBUG:
                print("Cost from all clusters old: ", cost_from_all_clusters_old, ", new: ", cost_from_all_clusters_new)
                
                print("times_not_changed: ", times_not_changed + 1)
            
            times_not_changed += 1
            medoids = copy(old_medoids)
        else:
            times_not_changed = 0
            
        # check if the middle points changed
        if i > 0:
            if not middlePointsChanged(old_medoids, medoids) and times_not_changed > G_MEDOIDS_NOT_CHANGED_LIMIT:
                print("medoids did not change, stopping the clustering, iteration:", i)
                g_iteration_counter = i + 1  # because the iteration starts from 0
                if G_DEBUG:
                    for y in range(len(medoids)):
                        print("old_medoids: ", old_medoids[y].m_coordinates, ", medoids: ", medoids[y].m_coordinates)
                break
            
    if G_DEBUG:
        print("Medoids with cluster number: ")
        for medoid in medoids:
            print(medoid.m_coordinates, " ", medoid.m_cluster_number)
            
    # assign each point to the nearest medoid (FINAL ASSIGNMENT)
    for l_point in l_points:
        min_distance = np.inf
        # for each point find the nearest medoid
        for medoid in medoids:
            dist = distance(l_point.m_coordinates, medoid.m_coordinates, 'm', int)
            if dist < min_distance:
                min_distance = dist
                l_point.m_cluster_number = medoid.m_cluster_number
                l_point.m_distance_from_middle = min_distance
    
    return medoids


def divisiveCentroid(l_points: list[point.Point], depth: int, seed_to_print: int | None):    
    global g_centroids_buffer
    global g_cluster_number_counter
    centroids: list[point.Point]
    centroids = []
    k = 2  # hard set for divisive clustering
    
    if G_DEBUG:
        print("Depth: ", depth)
    
    # init centroids
    while len(centroids) < k:
        random_point = copy(l_points[np.random.randint(0, len(l_points))])
        # check for duplicates
        if random_point in centroids:
            continue
        
        # check for close points
        # if the distance between the random point (future centroid) and any of the centroids is less than NUMBER, do not add the point and generate new centroid       
        is_okay = True
        for centroid in centroids:
            dist = distance(random_point.m_coordinates, centroid.m_coordinates, 'e2')
            
            if dist < G_CLOSE_MIDDLE_POINT_DISTANCE_CENTROID:
                is_okay = False
                break
                
        if is_okay:
            centroids.append(random_point)
        
    # plot init points with init centroids
    if depth == 0 and seed_to_print is not None:
        plotPoints(l_points, centroids, None, None, False, [], True, seed_to_print, "Divisive_clustering_(centroid)")
        
    # assign cluster number to each centroid
    for i in range(0, k):
        centroids[i].m_cluster_number = g_cluster_number_counter
        g_cluster_number_counter += 1
        
    if G_DEBUG:
        print("Init centroids:")
        for c in centroids:
            print("Cluster number: ", c.m_cluster_number, ", Coordinates: ", c.m_coordinates)
    
    # classify points to the nearest centroid
    old_centroids: list[point.Point]
    
    while True:
        # assign each point to the nearest centroid
        for l_point in l_points:
            min_distance = np.inf
            # for each point find the nearest centroid
            for centroid in centroids:
                dist = distance(l_point.m_coordinates, centroid.m_coordinates, 'e', int)
                if dist < min_distance:
                    min_distance = dist
                    l_point.m_cluster_number = centroid.m_cluster_number
                    l_point.m_distance_from_middle = min_distance

        # copy old centroids but not just references!
        old_centroids = []
        for centroid in centroids:
            old_centroids.append(copy(centroid))

        # update centroids
        for centroid in centroids:
            cluster_points = getPointsInOneCluster(l_points, centroid.m_cluster_number)
            new_centroid = np.mean([l_point.m_coordinates for l_point in cluster_points], axis=0, dtype=int)
            centroid.m_coordinates = new_centroid
            
        # check if the middle points changed
        if not middlePointsChanged(old_centroids, centroids):
            if G_DEBUG:
                print("Centroids did not change, stopping the clustering")
            break

    eval, bad_clusters_numbers = evaluateClustering(l_points, centroids)
    
    if G_DEBUG:
        print("Final centroids:")
        for c in centroids:
            print("Cluster number: ", c.m_cluster_number, ", Coordinates: ", c.m_coordinates)

    if eval:
        print("Clustering successful")
        print("Appending centroids to the buffer")
        for centroid in centroids:
            global g_centroids_buffer
            g_centroids_buffer.append(centroid)
    else:
        print("Clustering unsuccessful")
        print("Splitting the bad clusters")
        
        for centroid in centroids:
            if centroid.m_cluster_number not in bad_clusters_numbers:
                g_centroids_buffer.append(centroid)
        
        for bad_cluster_number in bad_clusters_numbers:
            cluster_points = getPointsInOneCluster(l_points, bad_cluster_number)
            divisiveCentroid(cluster_points, depth + 1, None)
            

def divisiveClustering(l_points: list[point.Point], seed_to_print: int):
    global g_centroids_buffer
    global g_cluster_number_counter
    g_centroids_buffer = []  # Reset the buffer
    g_cluster_number_counter = 0  # Reset the cluster number counter
     
    divisiveCentroid(l_points, 0, seed_to_print)
    
    if G_DEBUG:
        print("Centroids buffer:")
        for centroid in g_centroids_buffer:
            print(centroid.m_coordinates)


# for medoids
def getTotalCost(medoids: list[point.Point], all_points: list[point.Point]) -> int:
    all_cost: int = 0
    
    for medoid in medoids:
        cluster_points = getPointsInOneCluster(all_points, medoid.m_cluster_number)
        cost = getCostFromOneCluster(medoid, cluster_points)
        all_cost += cost
        
    return all_cost


# for medoids
# calculate the sum of mantahattan distances from the single point to all other points in cluster except itself (distance to itself is 0, so does not matter)
# cost => sum of distances
def getCostFromOneCluster(medoid: point.Point, cluster_points: list[point.Point]) -> int:
    cost: int = 0
    
    for l_point in cluster_points:
        cost += distance(medoid.m_coordinates, l_point.m_coordinates, 'm', int)
    
    return cost


def middlePointsChanged(old_middle_points: list[point.Point], new_middle_points: list[point.Point]) -> bool:
    for i in range(len(old_middle_points)):
        # if they do not have the same coordinates, they changed
        if not np.array_equal(old_middle_points[i].m_coordinates, new_middle_points[i].m_coordinates):
            if G_DEBUG:
                print("old_middle_point: ", old_middle_points[i].m_coordinates, ", new_middle_point: ", new_middle_points[i].m_coordinates)
            return True

    # if they have the same coordinates, they did not changed
    return False


# middle_points: centroids | medoids
# function to evaluate if the clustering was successful
# successful clustering: all points in single cluster have average distance from the middle point (centroid or medoid) less than 500 (G_SUCCESSFUL_DISTANCE) (use Euclidean distance)
def evaluateClustering(points: list[point.Point], middle_points: list[point.Point]) -> tuple[bool, list[int]]:
    bad_cluster_numbers: list[int] = []
    
    print("Bad middle points: ", end="")
    print_header: bool = True
    
    for middle_point in middle_points:
        cluster_points = getPointsInOneCluster(points, middle_point.m_cluster_number)
        
        # calculate mean of the distances from the middle point from single cluster
        mean_distance = np.mean([point.m_distance_from_middle for point in cluster_points])
        
        if mean_distance > G_SUCCESSFUL_DISTANCE:
            if print_header:
                print()  # new line
                print_header = False
            print("Distance:", mean_distance, ", Cluster:", middle_point.m_cluster_number, ", Middle point:", middle_point.m_coordinates)
            bad_cluster_numbers.append(middle_point.m_cluster_number)

    if len(bad_cluster_numbers) > 0:
        return False, bad_cluster_numbers
    
    print("None")
    return True, bad_cluster_numbers


def getPointsInOneCluster(points: list[point.Point], cluster_number: int) -> list[point.Point]:
    points_in_cluster: list[point.Point]
    points_in_cluster = []
    
    for p in points:
        if p.m_cluster_number == cluster_number:
            points_in_cluster.append(p)
            
    return points_in_cluster


# middle point: centroids | medoids
def plotPoints(points: list[point.Point], middle_points: list[point.Point], k: int | None, itertions: int | None, successful: bool, bad_clusters: list[int], init: bool, seed: int, middle_points_type: str):

    
    COLORS = [colorsys.hls_to_rgb(i / len(middle_points), 0.5, 1.0) for i in range(len(middle_points))]
    
    if G_DEBUG:
        print("COLORS: ", COLORS)
        print("Length of COLORS: ", len(COLORS))
    
    np.random.shuffle(COLORS)
    
    # setup high resolution plot
    fig = plt.figure(figsize=(28.8, 16.2), dpi=100)
    
    # get current timestamp in format YYYY-MM-DD---HH-MM-SS
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d---%H-%M-%S")
    
    if not init:
        if middle_points_type == "Divisive_clustering_(centroid)" and k is None and itertions is None:
            plt.title(f"Clustered points\nType: {middle_points_type}\nseed: {seed}\nclustering successful: {successful}\nnumber of bad clusters: {len(bad_clusters)}")
        else:
            plt.title(f"Clustered points\nType: {middle_points_type}\nseed: {seed}\nk: {k}\niterations count: {g_iteration_counter}/{itertions}\nclustering successful: {successful}\nnumber of bad clusters: {len(bad_clusters)}")
            
        # plot the points
        # for each point in bad cluster make separate x, y lists
        
        # filter points to bad and good clusters (bad clusters are the ones with average distance from the middle point greater than G_SUCCESSFUL_DISTANCE => 500)
        good_points = [p for p in points if p.m_cluster_number not in bad_clusters]
        bad_points = [p for p in points if p.m_cluster_number in bad_clusters]

        # extract coordinates
        points_x = [p.m_coordinates[0] for p in good_points]
        points_y = [p.m_coordinates[1] for p in good_points]

        # generate colors for the filtered points
        colors_good = [COLORS[p.m_cluster_number % len(COLORS)] for p in good_points]
        colors_bad = [COLORS[p.m_cluster_number % len(COLORS)] for p in bad_points]

        # plot the good points
        plt.scatter(points_x, points_y, color=colors_good)
        
        # plot the bad points only if there are any
        if len(bad_clusters) > 0:    
            points_x_bad = [p.m_coordinates[0] for p in bad_points]
            points_y_bad = [p.m_coordinates[1] for p in bad_points]
            plt.scatter(points_x_bad, points_y_bad, color=colors_bad, edgecolors='grey')

        # plot the middle points (centroids or medoids)
        [plt.scatter(middle_points[t].m_coordinates[0], middle_points[t].m_coordinates[1], facecolors='none', marker='o', s=100, edgecolors='black') for t in range(len(middle_points))]
    else:
        if middle_points_type == "Divisive_clustering_(centroid)":
            plt.title(f"Initial points\nType: {middle_points_type}\nseed: {seed}\nk: {k}")
        else:
            plt.title(f"Initial points\nType: {middle_points_type}\nseed: {seed}\nk: {k}\nmax iterations: {itertions}")
        # plot the points
        points_x = [p.m_coordinates[0] for p in points]
        points_y = [p.m_coordinates[1] for p in points]
        plt.scatter(points_x, points_y, color='red')
        # plot the middle points (centroids or medoids)
        [plt.scatter(middle_points[t].m_coordinates[0], middle_points[t].m_coordinates[1], facecolors='none', marker='o', s=100, edgecolors='black') for t in range(len(middle_points))]

    if init:
        plt.savefig(f"./plots/init_{middle_points_type}_{timestamp}.png", dpi=100, format='png')
        print("Init points plot saved to './plots/'")
    else:
        plt.savefig(f"./plots/clustered_{middle_points_type}_{timestamp}.png", dpi=100, format='png')
        print("Clustered points plot saved to './plots/'")
    
    plt.close(fig)

# middle_points: centroids | medoids
def runClustering(seed: int, k: int | None, iterations: int | None, choice: int):
    points = generatePoints(seed)
    
    if G_DEBUG:
        print("Unique points:", np.unique([p.m_coordinates for p in points], axis=0).shape[0])
    
    start: int
    end: int
    start = end = 0
    middle_points: list[point.Point]
    middle_points_type: str
    global g_iteration_counter
    g_iteration_counter = -1  # reset the global variable

    # k-means centroid
    if choice == 1:
        print("Clustering with k-means centroid:")
        start = time.time_ns()
        middle_points = kMeansCentroid(points, k, iterations, seed)
        end = time.time_ns()
        middle_points_type = "centroid"

    # k-means medoid
    elif choice == 2:
        print("Clustering with k-means medoid (optimized - pseudo implementation):")
        start = time.time_ns()
        middle_points = kMeansMedoidPseudo(points, k, iterations, seed)
        end = time.time_ns()
        middle_points_type = "medoid_optimized_pseudo"

    # divisive clustering centroid
    elif choice == 3:
        print("Clustering with divisive clustering centroid:")
        start = time.time_ns()
        divisiveClustering(points, seed)
        middle_points = copy(g_centroids_buffer)
        
        if G_DEBUG:
            print("Centroids buffer:")
            for middle_point in middle_points:
                print("Cluster number: ", middle_point.m_cluster_number, ", Coordinates: ", middle_point.m_coordinates)
        
        end = time.time_ns()
        middle_points_type = "Divisive_clustering_(centroid)"
        
    # k-means medoid NOT OPTIMIZED (real medoid implementation)
    elif choice == 4:
        print("Clustering with k-means medoid (real implementation):")
        start = time.time_ns()
        middle_points = kMeansMedoidReal(points, k, iterations, seed)
        end = time.time_ns()
        middle_points_type = "medoid_real_implementation"

    print(f"Time taken: {(end - start) // G_MILION} milliseconds")
    print("Evaluate clustering:")
    
    eval, bad_clusters = evaluateClustering(points, middle_points)
    
    if eval:
        print("Clustering successful")
        plotPoints(points, middle_points, k, iterations, True, bad_clusters, False, seed, middle_points_type)
    else:
        print("Clustering unsuccessful")
        plotPoints(points, middle_points, k, iterations, False, bad_clusters, False, seed, middle_points_type)

def main():
    if G_DEBUG:
        print("DEBUG MODE ON\nIf not intended, change global variable DEBUG to False\n")

    while True:
        print()  # new line
        choice_main = int(input("Enter choice:\n 0 - for EXIT\n 1 - k-means centroid\n 2 - k-means medoid (optimized - pseudo implementation)\n 3 - divisive clustering centroid\n 4 - k-means medoid (real implementation)\n"))
        if choice_main == 0:
            print("Exiting...")
            break
        elif choice_main > 4 or choice_main < 0:
            print("Invalid choice")
            continue
    
        seed = int(input("Enter seed (random number 0-100): "))
        if choice_main != 3:
            k = int(input("Enter k (recommended <=20): "))
            iterations = int(input("Enter max iterations: "))
        else:
            k = None  # hard set for divisive clustering (arbitrary set, it is hardcoded in the proper function)
            iterations = None  # not used for divisive clustering (set to arbitrary value)
        
        runClustering(seed, k, iterations, choice_main)
    

if __name__ == '__main__':
    global g_iteration_counter
    g_iteration_counter: int
    main()
