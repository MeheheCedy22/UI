import numpy as np


class Point:
    m_coordinates: np.ndarray
    m_cluster_number: int | None
    # distance from the "middle" of the cluster: centroid | medoid
    m_distance_from_middle: int | float | None

    def __init__(self, coordinates: np.ndarray, cluster_number: int | None, distance_from_middle: int | float | None):
        self.m_coordinates = coordinates
        self.m_cluster_number = cluster_number
        self.m_distance_from_middle = distance_from_middle
