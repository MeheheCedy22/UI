import farmer
import time
import random


class Generation:
    # m_ prefix is used to indicate that the variable is a member of the class
    m_max_genes: int
    m_generation_number: int
    m_farmers_count: int
    m_matrix_rows: int
    m_matrix_columns: int
    m_turn_genes_count: int

    m_fitness_through_generations: list[list[int]]
    m_farmers: list[farmer.Farmer]

    def __init__(self, farmers_count: int, max_genes: int, turn_genes: int, rows: int, columns: int, generation_number: int):
        self.m_max_genes = max_genes
        self.m_generation_number = generation_number
        self.m_farmers_count = farmers_count
        self.m_matrix_rows = rows
        self.m_matrix_columns = columns
        self.m_turn_genes_count = turn_genes

        self.m_fitness_through_generations = []

        self.m_farmers = []
        for farmer_number in range(0, self.m_farmers_count):
            self.m_farmers.append(farmer.Farmer(self.m_max_genes, self.m_turn_genes_count, self.m_matrix_rows, self.m_matrix_columns, farmer_number))

    @staticmethod
    def rouletteSelection(farmer_and_fitness: list[list[int]]) -> list[int]:
        seed = time.time_ns()
        random.seed(seed)

        l_sum = 0
        fitness_of_farmer_out: list[int]
        fitness_of_farmer_out = []
        temp_in = farmer_and_fitness.copy()

        for i in range(0, len(farmer_and_fitness)):
            l_sum += farmer_and_fitness[i][1]

        for _ in range(0, len(farmer_and_fitness) // 2):
            random_num = random.randint(0, l_sum - 1)
            current_sum = 0

            for j in range(0, len(temp_in)):

                current_sum += temp_in[j][1]
                if random_num < current_sum:
                    fitness_of_farmer_out.append(temp_in[j][0])
                    l_sum -= temp_in[j][1]

                    temp_in.pop(j)
                    break

        return fitness_of_farmer_out

    @staticmethod
    def fitnessOrder(fitness_and_farmer: list[list[int]]) -> list[int]:
        fitness_and_farmer_out: list[int]
        fitness_and_farmer_out = []

        for i in range(0, len(fitness_and_farmer) // 2):
            fitness_and_farmer_out.append(fitness_and_farmer[i][0])

        return fitness_and_farmer_out
