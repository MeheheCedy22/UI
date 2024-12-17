from direction import Direction as Dir 
import garden
import gene
import time
import random


class Farmer:
    # m_ prefix is used to indicate that the variable is a member of the class
    m_genes: gene.Gene
    m_garden: garden.Garden
    m_max_genes: int
    m_farmer_number: int
    m_fitness: int
    m_stones_count: int
    m_columns: int
    m_rows: int

    def __init__(self, max_genes: int, stones_count: int, rows: int, columns: int, farmer_number: int):
        self.m_max_genes = max_genes
        self.m_stones_count = stones_count
        self.m_rows = rows
        self.m_columns = columns
        self.m_genes = gene.Gene(self.m_max_genes, self.m_stones_count, self.m_rows, self.m_columns)
        self.m_garden = garden.Garden(self.m_rows, self.m_columns)
        self.m_fitness = 0
        self.m_farmer_number = farmer_number

    def mutateGene(self):
        seed = time.time_ns()
        random.seed(seed)

        for i in range(0, self.m_genes.m_max_size):
            # 1/1000 probability -> 0.1%
            probability = random.randint(0, 1000 - 1)

            if probability < 1:
                geneToMutate = random.randint(0, self.m_genes.m_max_size - 1)

                # emulating do-while loop
                x = random.randint(0, self.m_genes.m_n - 1)
                y = random.randint(0, self.m_genes.m_m - 1)

                while x != 0 and y != 0 and x != self.m_genes.m_n - 1 and y != self.m_genes.m_m - 1:
                    x = random.randint(0, self.m_genes.m_n - 1)
                    y = random.randint(0, self.m_genes.m_m - 1)

                self.m_genes.m_genes_vector[geneToMutate][0] = x
                self.m_genes.m_genes_vector[geneToMutate][1] = y

    def fitnessFunction(self):
        done = 0

        for i in range(0, self.m_garden.m_rows):
            for j in range(0, self.m_garden.m_columns):
                if self.m_garden.m_matrix[i][j] != 0 and self.m_garden.m_matrix[i][j] != -1:
                    done += 1

        self.m_fitness = done

    # it favors genes which are next to stones
    def fitnessFunctionForGene(self, gene_print_number: int) -> int:
        done = 0

        for i in range(0, self.m_garden.m_rows):
            for j in range(0, self.m_garden.m_columns):
                if self.m_garden.m_matrix[i][j] == gene_print_number:
                    # if is not on the edge
                    if i != 0 and j != 0 and i != self.m_garden.m_rows - 1 and j != self.m_garden.m_columns - 1:
                        # for each stone which is next add + 1 to indicate very good gene
                        if self.m_garden.m_matrix[i + 1][j] == -1:
                            done += 1
                        if self.m_garden.m_matrix[i - 1][j] == -1:
                            done += 1
                        if self.m_garden.m_matrix[i][j + 1] == -1:
                            done += 1
                        if self.m_garden.m_matrix[i][j - 1] == -1:
                            done += 1

                    done += 1

        return done

    def isFinal(self) -> bool:
        if self.m_fitness == (self.m_rows * self.m_columns) - self.m_stones_count:
            return True

        return False

    # value 1 is right, -1 is left
    @staticmethod
    def changeDirection(current_dir: Dir, value: int) -> Dir:
        if current_dir is Dir.RIGHT:
            if value == 1:
                return Dir.DOWN
            elif value == -1:
                return Dir.UP
            else:
                return Dir.ERROR
        elif current_dir is Dir.LEFT:
            if value == 1:
                return Dir.UP
            elif value == -1:
                return Dir.DOWN
            else:
                return Dir.ERROR
        elif current_dir is Dir.UP:
            if value == 1:
                return Dir.RIGHT
            elif value == -1:
                return Dir.LEFT
            else:
                return Dir.ERROR
        elif current_dir is Dir.DOWN:
            if value == 1:
                return Dir.LEFT
            elif value == -1:
                return Dir.RIGHT
            else:
                return Dir.ERROR
        else:
            return Dir.ERROR

    def canSwitchDir(self, local_dir: Dir, local_x: int, local_y: int) -> bool:
        if local_dir is Dir.RIGHT:
            # if there is no valid position in garden return false
            if local_y + 1 > self.m_garden.m_columns - 1:
                return False
            # if is valid and you can switch then switch directions
            if self.m_garden.m_matrix[local_x][local_y + 1] == 0:
                return True
        elif local_dir is Dir.LEFT:
            if local_y - 1 < 0:
                return False
            if self.m_garden.m_matrix[local_x][local_y - 1] == 0:
                return True
        elif local_dir is Dir.UP:
            if local_x - 1 < 0:
                return False
            if self.m_garden.m_matrix[local_x - 1][local_y] == 0:
                return True
        elif local_dir is Dir.DOWN:
            if local_x + 1 > self.m_garden.m_rows - 1:
                return False
            if self.m_garden.m_matrix[local_x + 1][local_y] == 0:
                return True
        else:
            return False

    @staticmethod
    def oppositeDir(local_dir: Dir) -> Dir:
        if local_dir is Dir.RIGHT:
            return Dir.LEFT
        elif local_dir is Dir.LEFT:
            return Dir.RIGHT
        elif local_dir is Dir.UP:
            return Dir.DOWN
        elif local_dir is Dir.DOWN:
            return Dir.UP
        else:
            return Dir.ERROR

    def walkGarden(self):
        printCounter = 1

        # initialize fitness array
        for i in range(0, self.m_max_genes):
            self.m_genes.m_genes_fitness.append([i, 0])

        for i in range(0, self.m_max_genes):
            local_x = self.m_genes.m_genes_vector[i][0]
            local_y = self.m_genes.m_genes_vector[i][1]
            hitCounter = 0
            doneWalkedLine = False
            lastX = -1
            lastY = -1

            local_dir = Dir.NONE

            # skip gene if farmer cant start walking from that position
            if self.m_garden.m_matrix[local_x][local_y] != 0:
                continue

            # get direction from which side farmer should go straight
            if local_x == 0:
                local_dir = Dir.DOWN
            elif local_x == self.m_garden.m_rows - 1:
                local_dir = Dir.UP
            elif local_y == 0:
                local_dir = Dir.RIGHT
            elif local_y == self.m_garden.m_columns - 1:
                local_dir = Dir.LEFT
            else:
                # ERROR
                return

            # while for walking in one direction
            while not doneWalkedLine:
                # if farmer is on the end of walkable line, terminate the while loop
                if local_dir is Dir.NONE or local_dir is Dir.ERROR or local_x > self.m_garden.m_rows - 1 or local_y > self.m_garden.m_columns - 1 or local_x < 0 or local_y < 0:
                    break

                # terminate if farmer circles around
                if lastX == local_x and lastY == local_y and hitCounter > 4 * self.m_genes.m_turn_genes_size:
                    break

                # switch equivalent
                if local_dir is Dir.RIGHT:
                    # if farmer is on the end of walkable line, terminate the while loop
                    if local_y + 1 > self.m_garden.m_columns - 1:
                        self.m_garden.m_matrix[local_x][local_y] = printCounter
                        doneWalkedLine = True
                        # z C++ by toto malo breaknut switch ale nevadi ked pouzijem continue
                        # lebo "switch" je na konci loopu aj tak
                        continue

                    # if farmer can go straight
                    if self.m_garden.m_matrix[local_x][local_y + 1] == 0:
                        self.m_garden.m_matrix[local_x][local_y] = printCounter
                        local_y += 1
                    # if farmer cant go straight, change direction
                    else:
                        temp_dir = self.changeDirection(local_dir, self.m_genes.m_turn_genes[hitCounter % self.m_genes.m_turn_genes_size])
                        if self.canSwitchDir(temp_dir, local_x, local_y):
                            local_dir = temp_dir
                        else:
                            temp_dir = self.oppositeDir(temp_dir)
                            if self.canSwitchDir(temp_dir, local_x, local_y):
                                local_dir = temp_dir
                            else:
                                return

                        hitCounter += 1
                        lastX = local_x
                        lastY = local_y

                elif local_dir is Dir.LEFT:
                    # if farmer is on the end of walkable line, terminate the while loop
                    if local_y - 1 < 0:
                        self.m_garden.m_matrix[local_x][local_y] = printCounter
                        doneWalkedLine = True
                        # z C++ by toto malo breaknut switch ale nevadi ked pouzijem continue
                        # lebo "switch" je na konci loopu aj tak
                        continue

                    # if farmer can go straight
                    if self.m_garden.m_matrix[local_x][local_y - 1] == 0:
                        self.m_garden.m_matrix[local_x][local_y] = printCounter
                        local_y -= 1
                    # if farmer cant go straight, change direction
                    else:
                        temp_dir = self.changeDirection(local_dir, self.m_genes.m_turn_genes[hitCounter % self.m_genes.m_turn_genes_size])
                        if self.canSwitchDir(temp_dir, local_x, local_y):
                            local_dir = temp_dir
                        else:
                            temp_dir = self.oppositeDir(temp_dir)
                            if self.canSwitchDir(temp_dir, local_x, local_y):
                                local_dir = temp_dir
                            else:
                                return

                        hitCounter += 1
                        lastX = local_x
                        lastY = local_y

                elif local_dir is Dir.UP:
                    # if farmer is on the end of walkable line, terminate the while loop
                    if local_x - 1 < 0:
                        self.m_garden.m_matrix[local_x][local_y] = printCounter
                        doneWalkedLine = True
                        # z C++ by toto malo breaknut switch ale nevadi ked pouzijem continue
                        # lebo "switch" je na konci loopu aj tak
                        continue

                    # if farmer can go straight
                    if self.m_garden.m_matrix[local_x - 1][local_y] == 0:
                        self.m_garden.m_matrix[local_x][local_y] = printCounter
                        local_x -= 1
                    # if farmer cant go straight, change direction
                    else:
                        temp_dir = self.changeDirection(local_dir, self.m_genes.m_turn_genes[hitCounter % self.m_genes.m_turn_genes_size])
                        if self.canSwitchDir(temp_dir, local_x, local_y):
                            local_dir = temp_dir
                        else:
                            temp_dir = self.oppositeDir(temp_dir)
                            if self.canSwitchDir(temp_dir, local_x, local_y):
                                local_dir = temp_dir
                            else:
                                return

                        hitCounter += 1
                        lastX = local_x
                        lastY = local_y

                elif local_dir is Dir.DOWN:
                    # if farmer is on the end of walkable line, terminate the while loop
                    if local_x + 1 > self.m_garden.m_rows - 1:
                        self.m_garden.m_matrix[local_x][local_y] = printCounter
                        doneWalkedLine = True
                        # z C++ by toto malo breaknut switch ale nevadi ked pouzijem continue
                        # lebo "switch" je na konci loopu aj tak
                        continue

                    # if farmer can go straight
                    if self.m_garden.m_matrix[local_x + 1][local_y] == 0:
                        self.m_garden.m_matrix[local_x][local_y] = printCounter
                        local_x += 1
                    # if farmer cant go straight, change direction
                    else:
                        temp_dir = self.changeDirection(local_dir, self.m_genes.m_turn_genes[hitCounter % self.m_genes.m_turn_genes_size])
                        if self.canSwitchDir(temp_dir, local_x, local_y):
                            local_dir = temp_dir
                        else:
                            temp_dir = self.oppositeDir(temp_dir)
                            if self.canSwitchDir(temp_dir, local_x, local_y):
                                local_dir = temp_dir
                            else:
                                return

                        hitCounter += 1
                        lastX = local_x
                        lastY = local_y
                else:
                    print("Error in walkGarden (pseudo switch)")
                    return

            # calculate fitness for specific gene
            gene_fitness = self.fitnessFunctionForGene(printCounter)

            # save fitness for specific gene to array of gene indexes with fitnesses
            self.m_genes.m_genes_fitness[i][1] = gene_fitness

            # toto ukazuje ktory gen pohrabal co ale nie je to uplne dokonale takze radsej comment
            # v ostatnyc hsituaciach kde je to potrebne to je zakomentovane
            # self.m_genes.m_genes_vector[i][2] = printCounter

            printCounter += 1
