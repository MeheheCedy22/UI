import time
import random
from typing import Tuple


class Gene:
    # m_ prefix is used to indicate that the variable is a member of the class
    m_genes_vector: list[list[int]]
    m_turn_genes: list[int]

    m_genes_fitness: list[list[int]]

    m_turn_genes_size: int
    m_max_size: int
    m_n: int
    m_m: int

    def __init__(self, size: int, turn_genes_size: int, n: int, m: int):
        self.m_max_size = size
        self.m_turn_genes_size = turn_genes_size
        self.m_n = n
        self.m_m = m

        self.m_turn_genes = []
        self.m_genes_vector = []
        self.m_genes_fitness = []

    def randomGenerateGenes(self, farmer_number: int):
        seed = time.time_ns() + farmer_number  # change seed with farmer number (so it is unique)
        random.seed(seed)

        generatedPairs: set[Tuple[int, int]]
        generatedPairs = set()

        while len(generatedPairs) < self.m_max_size:
            coinFlip: int
            coinFlipInner: int
            coinFlip = random.randint(0, 1)
            coinFlipInner = random.randint(0, 1)

            x: int
            y: int

            if coinFlip:
                x = random.randint(0, self.m_n - 1)

                if x == 0 or x == self.m_n - 1:
                    y = random.randint(0, self.m_m - 1)
                else:
                    y = self.m_m - 1 if coinFlipInner else 0
            else:
                y = random.randint(0, self.m_m - 1)

                if y == 0 or y == self.m_m - 1:
                    x = random.randint(0, self.m_n - 1)
                else:
                    x = self.m_n - 1 if coinFlipInner else 0

            if (x, y) not in generatedPairs:
                generatedPairs.add((x, y))
                self.m_genes_vector.append([x, y])
                # self.m_genes_vector.append([x, y, 'X'])

        for i in range(0, self.m_turn_genes_size):
            turn: int
            turn = random.randint(0, 1)
            if turn == 0:
                turn = -1
            self.m_turn_genes.append(turn)

    def printGenes(self):

        print("Genes")
        for gene in self.m_genes_vector:
            print("{" + f"{gene[0]}, {gene[1]}" + "}", end=' ')
            # print("{" + f"{gene[0]}, {gene[1]}" + "}" + f"({gene[2]})", end=' ')

        print("\nTurn genes")
        for turn_gene in self.m_turn_genes:
            print("{" + f"{turn_gene}" + "}", end=' ')
        print()
