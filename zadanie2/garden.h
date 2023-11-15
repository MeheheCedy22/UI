#ifndef UI_ZADANIE2A_GARDEN_H
#define UI_ZADANIE2A_GARDEN_H


#include <iostream>
#include <string>
#include <algorithm>
#include <vector>
#include <unordered_map>
#include <chrono>
#include <cstdlib>
#include <ctime>
#include <random>
#include <iomanip>
#include <set>


using namespace std::chrono;

using std::vector;
using std::set;
using std::pair;

using std::cin;
using std::cout;
using std::string;
using std::endl;


enum direction{
    RIGHT,
    LEFT,
    UP,
    DOWN,
    NONE,
    ERROR
};


class Garden{
public:

    int **matrix;
    int rows;
    int columns;

    Garden(int n, int m)
    {
        this->rows = n;
        this->columns = m;

        this->matrix = new int*[this->rows];

        for(int i=0; i< this->rows; i++)
        {
            this->matrix[i] = new int[this->columns];

            // fill the matrix with all zeros
            for(int j=0; j < this->columns; j++)
            {
                this->matrix[i][j] = 0;
            }
        }
    }

    ~Garden()
    {
        for(int i=0; i< this->rows; i++)
        {
            delete[] matrix[i];
            this->matrix[i] = nullptr;
        }

        delete[] matrix;
        matrix = nullptr;
    }

    void setStones(vector<vector<int>> stones)
    {
        for(unsigned int i=0; i<stones.size(); i++)
        {
            this->matrix[stones[i][0]][stones[i][1]] = -1;
        }
    }

    void printGarden()
    {
        for(int i=0; i<this->rows; i++)
        {
            for(int j=0; j<this->columns; j++)
            {
                if(this->matrix[i][j] != -1)
                {
                    cout << std::setw(2) << this->matrix[i][j] << " ";
                }
                else
                {
                    cout << std::setw(2) << "S" << " ";
                }
            }
            cout << '\n';
        }
    }
};

class Gene{
public:
    vector<vector<unsigned int>> genes_vector;
    vector<int> turn_genes;

    int turn_genes_size;
    int max_size;
    unsigned int n, m;

    Gene(int size, int turn_genes_size, int n, int m)
    {
        this->max_size = size;
        this->turn_genes_size = turn_genes_size;
        this->n = n;
        this->m = m;
    }

    void randomGenerateGene()
    {
        unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();

        std::default_random_engine generator(seed);
        std::uniform_int_distribution<int> x_distribution(0, this->n - 1);
        std::uniform_int_distribution<int> y_distribution(0, this->m - 1);

        set<pair<unsigned int, unsigned int>> generatedPairs;

        // this for loop make sure that there are no duplicates in the vector
        // and that the starting position is always on the edge of the garden
        for (int i = 0; i < this->max_size; )
        {
            unsigned coinFlip = x_distribution(generator) % 2;
            unsigned coinFlipInner = y_distribution(generator) % 2;

            unsigned int x, y;

            if(coinFlip)
            {
                x = x_distribution(generator);

                if(x == 0 || x == this->n-1)
                {
                    y = y_distribution(generator);
                }
                else
                {
                    y = (coinFlipInner) ? this->m - 1 : 0;
                }
            }
            else
            {
                y = y_distribution(generator);

                if(y == 0 || y == this->m-1)
                {
                    x = x_distribution(generator);
                }
                else
                {
                    x = (coinFlipInner) ? this->n - 1 : 0;
                }
            }

            // Check if the pair already exists
            if (generatedPairs.insert({x, y}).second)
            {
                // Pair is unique, add to vector
                this->genes_vector.push_back({x, y});
                ++i;  // Increment i only if a unique pair is added
            }
        }

        // also randomly generate turn genes

        for(int i=0; i<this->turn_genes_size; i++)
        {
            int x = x_distribution(generator) % 2;

            if(x == 0)
            {
                x = -1;
            }

            this->turn_genes.push_back(x);
        }
    }

    void printGenes()
    {
        cout << "Genes:\n";
        for(int i=0; i<this->max_size; i++)
        {
            cout << "{" << this->genes_vector[i][0] << "," << this->genes_vector[i][1] << "} ";
        }
        cout << '\n';
        if(turn_genes_size != 0)
        {
            cout << "Turn genes:\n";
            for(int i=0; i<this->turn_genes_size; i++)
            {
                cout << "{" << this->turn_genes[i] << "} ";
            }
            cout << '\n';
        }
    }
};


class Farmer{
public:
    Gene *genes;
    Garden *garden;
    int max_genes;
    int farmer_number;
    int fitness;
    int stones_count;
    int columns;
    int rows;

    Farmer(int max_genes, int stones_count, int rows, int columns, int farmer_number)
    {
        this->max_genes = max_genes;
        this->stones_count = stones_count;
        this->rows = rows;
        this->columns = columns;
        this->genes = new Gene(this->max_genes, this->stones_count, rows, columns);
        this->garden = new Garden(rows, columns);
        this->fitness = 0;
        this->farmer_number = farmer_number;
    }

    ~Farmer()
    {
        delete garden;
        delete genes;
        genes = nullptr;
        garden = nullptr;
    }

    void mutateGene()
    {
        unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();
        srand(seed);

        for(int i = 0; i < this->genes->max_size; i++)
        {
            unsigned int probability = rand() % 100;

            // comparing variable means how many % chance there is for mutation
            if(probability < 25)
            {
                unsigned int geneToMutate = rand() % this->genes->max_size;
                unsigned int x;
                unsigned int y;

                do
                {
                    x = rand() % this->genes->n;
                    y = rand() % this->genes->m;
                }
                while(x != 0 && y != 0 && x != this->genes->n-1 && y != this->genes->m-1);

                this->genes->genes_vector[geneToMutate][0] = x;
                this->genes->genes_vector[geneToMutate][1] = y;
            }
        }
    }

    vector<unsigned int> rouletteSelection(vector<vector<int>> fitness_and_farmer)
    {
        unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();
        srand(seed);

        unsigned int sum = 0;
        vector<unsigned int> fitness_and_farmer_out;
        vector<vector<int>> temp_in = fitness_and_farmer;


        for(int i= 0; i < temp_in.size(); i++)
        {
            sum += temp_in[i][1];
        }

        // Roulette wheel selection
        for(int i = 0; i < fitness_and_farmer.size() / 2; i++)
        {
            int random_num = rand() % sum;
            int current_sum = 0;

            // Find the selected individual based on the random number
            for (int j = 0; j < temp_in.size(); j++)
            {
                current_sum += temp_in[j][1];
                if (random_num < current_sum)
                {
                    fitness_and_farmer_out.push_back(temp_in[j][0]);
                    sum = sum - temp_in[j][1];
/*testing*/
//                    cout << "index: " << temp_in[j][0] << " fitness: " << temp_in[j][1] << '\n';
/*------------*/
                    temp_in.erase(temp_in.begin() + j);
                    break;
                }
            }
        }


        return fitness_and_farmer_out;
    }

    vector<unsigned int> fitnessOrder(vector<vector<int>> fitness_and_farmer)
    {
        vector<unsigned int> fitness_and_farmer_out;

        for(int i=0; i < fitness_and_farmer.size() / 2; i++)
        {
            fitness_and_farmer_out.push_back(fitness_and_farmer[i][0]);
/*testing*/
//            cout << "index: " << fitness_and_farmer[i][0] << " fitness: " << fitness_and_farmer[i][1] << '\n';
/*------------*/
        }

        return fitness_and_farmer_out;
    }

    // how many squares are done
    void fitnessFunction()
    {
        int done = 0;

        for(int i=0; i<this->garden->rows; i++)
        {
            for(int j=0; j< this->garden->columns; j++)
            {
                if(this->garden->matrix[i][j] != 0 && this->garden->matrix[i][j] != -1)
                {
                    done++;
                }
            }
        }

        this->fitness = done;
    }

    bool isFinal()
    {
        if(this->fitness == (this->rows * this->columns) - this->stones_count)
        {
            return true;
        }

        return false;
    }

    // value 1 is right, -1 is left
    direction changeDirection(direction current_dir, int value)
    {
        switch(current_dir)
        {
            case RIGHT:
                if(value == 1)
                {
                    return DOWN;
                }
                else if(value == -1)
                {
                    return UP;
                }
                else
                {
                    return ERROR;
                }
            case LEFT:
                if(value == 1)
                {
                    return UP;
                }
                else if(value == -1)
                {
                    return DOWN;
                }
                else
                {
                    return ERROR;
                }
            case UP:
                if(value == 1)
                {
                    return RIGHT;
                }
                else if(value == -1)
                {
                    return LEFT;
                }
                else
                {
                    return ERROR;
                }
            case DOWN:
                if(value == 1)
                {
                    return LEFT;
                }
                else if(value == -1)
                {
                    return RIGHT;
                }
                else
                {
                    return ERROR;
                }
            default:
                return ERROR;
        }
    }

    bool canSwitchDir(direction dir, int localX, int localY)
    {
        switch(dir)
        {
            case RIGHT:
                // if there is no valid position in garden return false
                if(localY+1 > this->garden->columns-1)
                {
                    return false;
                }

                // if is valid and you can switch then switch directions
                if(this->garden->matrix[localX][localY+1] == 0)
                {
                    return true;
                }
                break;
            case LEFT:
                if(localY-1 < 0)
                {
                    return false;
                }

                if(this->garden->matrix[localX][localY-1] == 0)
                {
                    return true;
                }
                break;
            case UP:
                if(localX-1 < 0)
                {
                    return false;
                }

                if(this->garden->matrix[localX-1][localY] == 0)
                {
                    return true;
                }
                break;
            case DOWN:
                if(localX+1 > this->garden->rows-1)
                {
                    return false;
                }

                if(this->garden->matrix[localX+1][localY] == 0)
                {
                    return true;
                }
                break;
            default:
                return false;
        }

        return false;
    }

    direction oppositeDir(direction dir)
    {
        switch(dir)
        {
            case RIGHT:
                return LEFT;
            case LEFT:
                return RIGHT;
            case UP:
                return DOWN;
            case DOWN:
                return UP;
            default:
                return ERROR;
        }
    }

    void walkGarden()
    {
/*testing*/
//        cout << "walkGarden for One farmer, printGnes: \n";
//        this->genes->printGenes();
/*------------*/
        unsigned int printCounter = 1;

        for(int i=0; i < this->max_genes; i++)
        {
            int localX = this->genes->genes_vector[i][0];
            int localY = this->genes->genes_vector[i][1];
            unsigned int hitCounter = 0;
            bool doneWalkedLine = false;
            int lastX = -1;
            int lastY = -1;


            // skip gene if farmer cant start walking from that position
            if(this->garden->matrix[localX][localY] != 0)
            {
               continue;
            }

            direction dir = NONE;

            // get direction from which side farmer should go straight
            if(localX == 0)
            {
                dir = DOWN;
            }
            else if (localX == this->garden->rows-1)
            {
                dir = UP;
            }
            else if (localY == 0)
            {
                dir = RIGHT;
            }
            else if (localY == this->garden->columns-1)
            {
                dir = LEFT;
            }
            else
            {
                // ERROR
                return;
            }
/*testing*/
//            cout << "dir: " << dir << '\n';
//            cout << "local X: " << localX << '\n';
//            cout << "local Y: " << localY << '\n';
//            cout << "i: " << i << '\n';
//            cout << "print counter: " << printCounter << '\n';
//            cout << "before while\n";
/*------------*/

            // while for walking in one direction
            while(!doneWalkedLine)
            {
                // if farmer is on the end of walkable line, terminate the while loop
                if(dir == NONE || dir == ERROR || localX > this->garden->rows-1 || localY > this->garden->columns-1 || localX < 0 || localY < 0)
                {
                    break;
                }

                // terminate if farmer circles around
                if(lastX == localX && lastY == localY && hitCounter > this->genes->turn_genes_size)
                {
                    return;
                }
/*testing*/
//                cout << "dir: " << dir << '\n';
//                cout << "local X: " << localX << '\n';
//                cout << "local Y: " << localY << '\n';
//                cout << "i: " << i << '\n';
/*------------*/
                switch(dir)
                {
                    case RIGHT:
                        // if farmer is on the end of walkable line, terminate the while loop
                        if(localY+1 > this->garden->columns-1)
                        {
                            this->garden->matrix[localX][localY] = printCounter;
                            doneWalkedLine = true;
                            break;
                        }
                        // if farmer can go straight
                        if(this->garden->matrix[localX][localY+1] == 0)
                        {
                            this->garden->matrix[localX][localY] = printCounter;
                            ++localY;
                        }
                        // if farmer cant go straight, change direction
                        else
                        {
                            direction temp_dir = changeDirection(dir, this->genes->turn_genes[hitCounter % this->genes->turn_genes_size]);
                            if(canSwitchDir(temp_dir, localX, localY))
                            {
                                dir = temp_dir;
                            }
                            else
                            {
                                temp_dir = oppositeDir(temp_dir);
                                if(canSwitchDir(temp_dir, localX, localY))
                                {
                                    dir = temp_dir;
                                }
                                else
                                {
                                    return;
                                }
                            }

                            hitCounter++;
                            lastX = localX;
                            lastY = localY;
                        }
                        break;
                    case LEFT:
                        // if farmer is on the end of walkable line, terminate the while loop
                        if(localY-1 < 0)
                        {
                            this->garden->matrix[localX][localY] = printCounter;
                            doneWalkedLine = true;
                            break;
                        }
                        // if farmer can go straight
                        if(this->garden->matrix[localX][localY-1] == 0)
                        {
                            this->garden->matrix[localX][localY] = printCounter;
                            --localY;
                        }
                        // if farmer cant go straight, change direction
                        else
                        {
                            direction temp_dir = changeDirection(dir, this->genes->turn_genes[hitCounter % this->genes->turn_genes_size]);
                            if(canSwitchDir(temp_dir, localX, localY))
                            {
                                dir = temp_dir;
                            }
                            else
                            {
                                temp_dir = oppositeDir(temp_dir);
                                if(canSwitchDir(temp_dir, localX, localY))
                                {
                                    dir = temp_dir;
                                }
                                else
                                {
                                    return;
                                }
                            }

                            hitCounter++;
                            lastX = localX;
                            lastY = localY;
                        }
                        break;
                    case UP:
                        // if farmer is on the end of walkable line, terminate the while loop
                        if(localX-1 < 0)
                        {
                            this->garden->matrix[localX][localY] = printCounter;
                            doneWalkedLine = true;
                            break;
                        }
                        // if farmer can go straight
                        if(this->garden->matrix[localX-1][localY] == 0)
                        {
                            this->garden->matrix[localX][localY] = printCounter;
                            --localX;
                        }
                        // if farmer cant go straight, change direction
                        else
                        {
                            direction temp_dir = changeDirection(dir, this->genes->turn_genes[hitCounter % this->genes->turn_genes_size]);
                            if(canSwitchDir(temp_dir, localX, localY))
                            {
                                dir = temp_dir;
                            }
                            else
                            {
                                temp_dir = oppositeDir(temp_dir);
                                if(canSwitchDir(temp_dir, localX, localY))
                                {
                                    dir = temp_dir;
                                }
                                else
                                {
                                    return;
                                }
                            }

                            hitCounter++;
                            lastX = localX;
                            lastY = localY;
                        }
                        break;
                    case DOWN:
                        // if farmer is on the end of walkable line, terminate the while loop
                        if(localX+1 > this->garden->rows-1)
                        {
                            this->garden->matrix[localX][localY] = printCounter;
                            doneWalkedLine = true;
                            break;
                        }
                        // if farmer can go straight
                        if(this->garden->matrix[localX+1][localY] == 0)
                        {
                            this->garden->matrix[localX][localY] = printCounter;
                            ++localX;
                        }
                        // if farmer cant go straight, change direction
                        else
                        {
                            direction temp_dir = changeDirection(dir, this->genes->turn_genes[hitCounter % this->genes->turn_genes_size]);
                            if(canSwitchDir(temp_dir, localX, localY))
                            {
                                dir = temp_dir;
                            }
                            else
                            {
                                temp_dir = oppositeDir(temp_dir);
                                if(canSwitchDir(temp_dir, localX, localY))
                                {
                                    dir = temp_dir;
                                }
                                else
                                {
                                    return;
                                }
                            }

                            hitCounter++;
                            lastX = localX;
                            lastY = localY;
                        }
                        break;
                    default:
                        dir = NONE;
                }
            }
/*testing*/
//            this->garden->printGarden();
//            cout << "after while\n";
/*------------*/
            printCounter++;
        }
/*testing*/
//        this->garden->printGarden();
/*------------*/
    }
};

class Generation{
public:
    int max_genes;
    int generation_number;
    int farmers_count;
    int matrix_rows;
    int matrix_columns;
    int turn_genes_count;

    // what is in the fitness_through_generations vector:
    // farmer number, fitness for that farmer
    vector<vector<int>> fitness_through_generations;
    vector<Farmer*> farmer;

    Generation(int farmers_count, int max_genes, int turn_genes, int rows, int columns, int generation_number)
    {
        this->max_genes = max_genes;
        this->generation_number = generation_number;
        this->farmers_count = farmers_count;
        this->matrix_rows = rows;
        this->matrix_columns = columns;
        this->turn_genes_count = turn_genes;

        for(int i=0; i<farmers_count; i++)
        {
            Farmer *f = new Farmer(this->max_genes, this->turn_genes_count, this->matrix_rows, this->matrix_columns, i);
            this->farmer.push_back(f);
        }
    }

    ~Generation()
    {
        for(int i=0; i<this->farmers_count; i++)
        {
            delete farmer[i];
            farmer[i] = nullptr;
        }
    }
};


#endif //UI_ZADANIE2A_GARDEN_H
