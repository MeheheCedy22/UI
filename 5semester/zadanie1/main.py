import time
import random

import generation as gen

# GLOBAL VARIABLES
evolution_number = 0
evolution_count = 100
print_setup = False
# -------------------
rows: int
columns: int
stones_count: int
max_genes: int
number_of_generations: int
number_of_farmers_in_generation: int
stones: list[list[int]]
generations: list[gen.Generation]
print_min_max_avg: int
show_fittness_higher_than: int
saved_rows: int
saved_columns: int
saved_stones_count: int
saved_max_genes: int
saved_number_of_generations: int
saved_number_of_farmers_in_generation: int
saved_stones: list[list[int]]
saved_print_min_max_avg: int
saved_show_fittness_higher_than: int
# -------------------


def printSetup():
    global rows, columns, stones_count, max_genes
    global number_of_generations, evolution_count
    global number_of_farmers_in_generation, stones
    global print_min_max_avg, show_fittness_higher_than
    global evolution_number

    print('----------Program Setup----------')
    print("Number of evolutions: ", evolution_count)
    print('Number of generations: ', number_of_generations)
    print('Number of farmers in generation: ', number_of_farmers_in_generation)
    print('Max genes: ', max_genes)
    print('Number of stones: ', stones_count)
    print('Rows: ', rows)
    print('Columns: ', columns)
    print('Stones: ', stones)
    for i in range(0, rows):
        for j in range(0, columns):
            if [i, j] in stones:
                print('S', end=' ')
            else:
                print('0', end=' ')
        print()
    print()


def compute():
    global saved_rows, saved_columns, saved_stones_count, saved_max_genes
    global saved_number_of_generations, number_of_farmers_in_generation
    global saved_number_of_farmers_in_generation, saved_stones
    global saved_print_min_max_avg, saved_show_fittness_higher_than
    global evolution_number, generations, stones
    global print_setup, show_fittness_higher_than, print_min_max_avg
    global rows, columns, stones_count, max_genes, number_of_generations

    evolution_number += 1

    generation: gen
    generation = gen.Generation(number_of_farmers_in_generation, max_genes, stones_count, rows, columns, 0)
    generations.append(generation)

    if print_setup and evolution_number == 1:
        printSetup()

    print("Evolution number: ", evolution_number)

    for i in range(0, number_of_generations):

        if i != 0:
            # uses sorted vector of fitness to select parents from previous generation
            seed: int
            seed = time.time_ns()
            random.seed(seed)
            coinFlip: int
            coinFlip = random.randint(0, 1)
            indexes: list[int]

            # uses already sorted vector of integers
            # gets indexes of half of the farmers in previous generation
            # then uses those indexes to get the genes of those farmers
            # then crossover
            if coinFlip:
                # roulette selection
                indexes = generations[i].rouletteSelection(generations[i - 1].m_fitness_through_generations)
            else:
                # fitnessOrder selection (the best by fitness)
                indexes = generations[i].fitnessOrder(generations[i - 1].m_fitness_through_generations)

            # cross-over
            # create new genes for farmer

            for k in range(0, len(indexes)):
                # pick 3 parents, first, second, last
                parent1 = generations[i - 1].m_farmers[indexes[k]].m_genes
                parent2 = generations[i - 1].m_farmers[indexes[(k + 1) % len(indexes)]].m_genes
                parent3 = generations[i - 1].m_farmers[indexes[-k - 1]].m_genes

                for gene_index in range(0, max_genes):
                    # select specific gene from parent
                    pos_gene1 = parent1.m_genes_vector[gene_index]
                    pos_gene2 = parent2.m_genes_vector[gene_index]
                    pos_gene3 = parent3.m_genes_vector[gene_index]

                    # if parent1 has higher fitness than parent2, then select gene from parent1, else from parent2
                    if parent1.m_genes_fitness[gene_index] > parent2.m_genes_fitness[gene_index]:
                        generations[i].m_farmers[k * 2 + 0].m_genes.m_genes_vector.append(pos_gene1)
                    else:
                        generations[i].m_farmers[k * 2 + 0].m_genes.m_genes_vector.append(pos_gene2)

                    # if parent1 has higher fitness than parent3, then select gene from parent1, else from parent3
                    if parent1.m_genes_fitness[gene_index] > parent3.m_genes_fitness[gene_index]:
                        generations[i].m_farmers[k * 2 + 1].m_genes.m_genes_vector.append(pos_gene1)
                    else:
                        generations[i].m_farmers[k * 2 + 1].m_genes.m_genes_vector.append(pos_gene3)

                    # Set printNumber for the gene as X to reset it
                    # generations[i].m_farmers[k * 2 + 0].m_genes.m_genes_vector[-1][2] = 'x'
                    # generations[i].m_farmers[k * 2 + 1].m_genes.m_genes_vector[-1][2] = 'x'

            # for turn genes copy from first parent
            # it is done this way because it basically does not matter that much, it could be basically random and performance would be the same
            for x in range(0, number_of_farmers_in_generation):
                for o in range(0, stones_count):
                    generations[i].m_farmers[x].m_genes.m_turn_genes.append(
                        generations[i - 1].m_farmers[indexes[0]].m_genes.m_turn_genes[o])

        # iterate through all farmers in generation
        for j in range(0, number_of_farmers_in_generation):
            # only first generation gets random genes
            if i == 0:
                generations[i].m_farmers[j].m_genes.randomGenerateGenes(farmer_number=j)

            # mutation (probability is done in the function)
            generations[i].m_farmers[j].mutateGene()

            generations[i].m_farmers[j].m_garden.setStones(stones)

            # fitness for genes is called inside walkGarden()
            generations[i].m_farmers[j].walkGarden()
            generations[i].m_farmers[j].fitnessFunction()
            # sort genes by fitness format: (index, fitness)
            generations[i].m_farmers[j].m_genes.m_genes_fitness.sort(key=lambda lam: lam[1], reverse=True)
            generations[i].m_fitness_through_generations.append([j, generations[i].m_farmers[j].m_fitness])

            if generations[i].m_farmers[j].isFinal():
                print('Solution: ')
                print(f'Evolution: {evolution_number} Generation: {generations[i].m_generation_number} Farmer: {generations[i].m_farmers[j].m_farmer_number}')
                generations[i].m_farmers[j].m_genes.printGenes()
                generations[i].m_farmers[j].m_garden.printGarden()
                print()

                return True

        maximum: int
        minimum: int
        average: int
        suma: int
        suma = average = 0
        maximum = minimum = generations[i].m_fitness_through_generations[0][1]

        for y in range(0, len(generations[i].m_fitness_through_generations)):
            if generations[i].m_fitness_through_generations[y][1] > maximum:
                maximum = generations[i].m_fitness_through_generations[y][1]
            elif generations[i].m_fitness_through_generations[y][1] < minimum:
                minimum = generations[i].m_fitness_through_generations[y][1]

            suma += generations[i].m_fitness_through_generations[y][1]

        average = int(suma / len(generations[i].m_fitness_through_generations))

        # print data for fitness graph only if option selected or manually set
        if print_min_max_avg:
            # if first generation print header
            if i == 0:
                print('GenNum\tMin\tMax\tAvg')
            
            # optional, to see only generations with fitness higher than X
            if maximum > show_fittness_higher_than:
                print(f'{generations[i].m_generation_number}\t{minimum}\t{maximum}\t{average}')

        # if converges (fitness is the same for all farmers in generation) then stop
        if minimum == maximum and maximum == average:
            return False

        # sort farmers by fitness in descending order in the vector in generation
        generations[i].m_fitness_through_generations.sort(key=lambda lam: lam[1], reverse=True)

        # create next generation
        if i != number_of_generations - 1:
            next_generation: gen.Generation
            next_generation = gen.Generation(number_of_farmers_in_generation, max_genes, stones_count, rows, columns, i + 1)
            generations.append(next_generation)

    return False


def manual_input():
    global show_fittness_higher_than, print_min_max_avg, rows, columns, stones_count, max_genes
    global number_of_generations, number_of_farmers_in_generation, stones, generations, print_setup
    rows = columns = stones_count = max_genes = number_of_generations = number_of_farmers_in_generation = 0

    # 2D vector to store stone positions
    stones = []
    generations = []

    # MANUAL INPUT
    choice = int(input('Enter 0 for automatic input or 1 for manual input: '))
    print_min_max_avg = int(input('If you wish to print min, max, average fitness values for the generation -> enter 1, else 0: '))
    print()

    if print_min_max_avg:
        show_fittness_higher_than = int(input('Enter the minimum fitness value to be shown (from the max values): '))
        print()
    else:
        show_fittness_higher_than = 0
    # -------------------
    # FOR DEBUGGING (AUTOMATED)
    # TODO comment out
    #     choice = 0
    #     print_min_max_avg = 1
    # -------------------

    generations.clear()
    if not choice:
        rows = 10
        columns = 12
        stones_count = 6
        number_of_generations = 1024  # infinity (it will stop when it finds solution, or when evolution count is reached)
        number_of_farmers_in_generation = 256
        stones = [[1, 5], [2, 1], [3, 4], [4, 2], [6, 8], [6, 9]]
        print_setup = True
    elif choice:
        rows = int(input('Enter the number of rows in the matrix: '))
        columns = int(input('Enter the number of columns in the matrix: '))
        print("Number of generations is set to infinity (it will stop when it finds solution, or when evolution count is reached)")
        # number_of_generations = int(input('Enter number of generations (recommended 128-256): '))
        number_of_generations = 1024  # infinity (it will stop when it finds solution, or when evolution count is reached)
        number_of_farmers_in_generation = int(input('Enter number of farmers in generation (use powers of 2 that are greater than 8, recommended 256 or 128): '))
        stones_count = int(input('Enter number of stones (at least 1): '))

        if stones_count < 1:
            print('Invalid number of stones')
            return False
        else:
            print("Indexing start from 0")
            print("Possible stone positions (from assignment):")
            print("1 5")
            print("2 1")
            print("3 4")
            print("4 2")
            print("6 8")
            print("6 9")
            print(f"Range: (0,0) ({rows - 1},{columns - 1})")

        for i in range(0, stones_count):
            x: int
            y: int
            x = int(input(f'Enter x coordinate of stone {i + 1}: '))
            y = int(input(f'Enter y coordinate of stone {i + 1}: '))

            if x < 0 or x >= rows or y < 0 or y >= columns:
                print('Invalid stone position')
                return False
            else:
                stones.append([x, y])
    else:
        print('Wrong input')
        return False

    max_genes = rows + columns


def save_input():
    global rows, columns, stones_count, max_genes
    global number_of_generations
    global number_of_farmers_in_generation, stones, generations
    global print_min_max_avg, show_fittness_higher_than
    global saved_rows, saved_columns, saved_stones_count, saved_max_genes
    global saved_number_of_generations
    global saved_number_of_farmers_in_generation, saved_stones
    global saved_print_min_max_avg, saved_show_fittness_higher_than
    saved_rows = rows
    saved_columns = columns
    saved_stones_count = stones_count
    saved_max_genes = max_genes
    saved_number_of_generations = number_of_generations
    saved_number_of_farmers_in_generation = number_of_farmers_in_generation
    saved_stones = stones
    saved_print_min_max_avg = print_min_max_avg
    saved_show_fittness_higher_than = show_fittness_higher_than


def reset():
    global rows, columns, stones_count, max_genes
    global number_of_generations
    global number_of_farmers_in_generation, stones, generations
    global print_min_max_avg, show_fittness_higher_than
    global saved_rows, saved_columns, saved_stones_count, saved_max_genes
    global saved_number_of_generations
    global saved_number_of_farmers_in_generation, saved_stones
    global saved_print_min_max_avg, saved_show_fittness_higher_than
    
    rows = saved_rows
    columns = saved_columns
    stones_count = saved_stones_count
    max_genes = saved_max_genes
    number_of_generations = saved_number_of_generations
    number_of_farmers_in_generation = saved_number_of_farmers_in_generation
    stones = saved_stones
    generations.clear()
    print_min_max_avg = saved_print_min_max_avg
    show_fittness_higher_than = saved_show_fittness_higher_than


# FOR DEBUGGING
def printVars():
    print()
    print()
    print(f"rows = {rows}")
    print(f"columns = {columns}")
    print(f"stones_count = {stones_count}")
    print(f"max_genes = {max_genes}")
    print(f"number_of_generations = {number_of_generations}")
    print(f"number_of_farmers_in_generation = {number_of_farmers_in_generation}")
    print(f"stones = {stones}")
    print(f"generations = {generations}")
    print(f"print_min_max_avg = {print_min_max_avg}")
    print(f"print_min_max_avg = {print_min_max_avg}")
    print(f"show_fittness_higher_than = {show_fittness_higher_than}")
    print()
    print()


if __name__ == '__main__':
    manual_input()
    save_input()

    result: bool
    result = False
    while not result and evolution_number < evolution_count:
        reset()
        # printVars()
        result = compute()

    if result:
        print('Found solution')
    else:
        print('Did not find solution')
