class Garden:
    # m_ prefix is used to indicate that the variable is a member of the class
    m_matrix: list[list[int]]
    m_rows: int
    m_columns: int

    def __init__(self, n: int, m: int):
        self.m_rows = n
        self.m_columns = m
        self.m_matrix = [[0 for _ in range(m)] for _ in range(n)]

    # Destructor not needed, reason Python

    def setStones(self, stones: list[list[int]]):
        for stone in stones:
            self.m_matrix[stone[0]][stone[1]] = -1

    def printGarden(self):
        for i in range(self.m_rows):
            for j in range(self.m_columns):
                if self.m_matrix[i][j] != -1:
                    print(f'{self.m_matrix[i][j]:2}', end=' ')
                else:
                    print(f' S', end=' ')

            print()
        print()
