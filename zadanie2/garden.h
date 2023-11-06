#pragma clang diagnostic push
#pragma ide diagnostic ignored "cert-msc50-cpp"
#pragma ide diagnostic ignored "cert-msc51-cpp"
#pragma ide diagnostic ignored "google-explicit-constructor"
#pragma ide diagnostic ignored "modernize-loop-convert"
#pragma ide diagnostic ignored "readability-make-member-function-const"
#pragma ide diagnostic ignored "modernize-use-auto"
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

using namespace std::chrono;

using std::vector;
using std::cin;
using std::cout;
using std::endl;
using std::string;


// default direction when wall is hit is right
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
        for(int i=0; i<stones.size(); i++)
        {
            this->matrix[stones[i][0]][stones[i][1]] = -1;
        }
    }

    void setPath(int x, int y, int value)
    {
        this->matrix[x][y] = value;
    }

    void printGarden()
    {
        for(int i=0; i<this->rows; i++)
        {
            for(int j=0; j<this->columns; j++)
            {
                if(this->matrix[i][j] != -1)
                {
                    cout << this->matrix[i][j] << " ";
                }
                else
                {
                    cout << "S" << " ";
                }
            }
            cout << endl;
        }
    }

    void processGarden()
    {

    }
};

class Gene{
public:
    vector<vector<unsigned int>> genes_vector;
    int max_size;
    int n, m;

    Gene(int size, int n, int m)
    {
        this->max_size = size;
        this->n = n;
        this->m = m;
    }

    ~Gene()
    {
        genes_vector.clear();
    }

    void randomGenerateGene()
    {
        unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();
        std::default_random_engine generator(seed);
        std::uniform_int_distribution<int> x_distribution(0, this->n - 1);
        std::uniform_int_distribution<int> y_distribution(0, this->m - 1);

        for (int i = 0; i < this->max_size; i++)
        {
            unsigned int x = x_distribution(generator);
            unsigned int y = y_distribution(generator);

            this->genes_vector.push_back({x, y});
        }
    }

    static Gene mutateGene(Gene g)
    {
        srand(time(nullptr)); // NOLINT(*-msc51-cpp)

        // there is 5% chance to mutate 1 random gene

        return g;
    }

    static Gene crossover(Gene g1, Gene g2)
    {
        Gene new_gene = g1;


        return new_gene;
    }

    void printGenes()
    {
        cout << "Genes: " << endl;
        for(int i=0; i<this->max_size; i++)
        {
            cout << "{" << this->genes_vector[i][0] << "," << this->genes_vector[i][1] << "} ";
        }
        cout << endl;
    }
};


class Farmer{
public:
    Gene *genes;
    Garden *garden;
    int max_genes;
    int farmer_number;
    int fitness;

    Farmer(int max_genes, int rows, int columns, int farmer_number)
    {
        this->max_genes = max_genes;
        this->genes = new Gene(this->max_genes, rows, columns);
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


    /* pravdepodobne treba fix, lebo netusim co to robi */
    // farmer are going straight until they hit an obstacle (stone or done path), then they go left or right
    // farmer always wants to go to the right, if cant then left
    void moveFarmer(int x, int y, direction dir) {
        if (dir == RIGHT) {
            if (x + 1 < this->garden->rows && this->garden->matrix[x + 1][y] == 0) {
                this->garden->matrix[x + 1][y] = this->garden->matrix[x][y] + 1;
                moveFarmer(x + 1, y, RIGHT);
            } else if (y + 1 < this->garden->columns && this->garden->matrix[x][y + 1] == 0) {
                this->garden->matrix[x][y + 1] = this->garden->matrix[x][y] + 1;
                moveFarmer(x, y + 1, RIGHT);
            } else if (x - 1 >= 0 && this->garden->matrix[x - 1][y] == 0) {
                this->garden->matrix[x - 1][y] = this->garden->matrix[x][y] + 1;
                moveFarmer(x - 1, y, RIGHT);
            } else if (y - 1 >= 0 && this->garden->matrix[x][y - 1] == 0) {
                this->garden->matrix[x][y - 1] = this->garden->matrix[x][y] + 1;
                moveFarmer(x, y - 1, RIGHT);
            } else {
                // farmer is stuck
                return;
            }
        } else if (dir == LEFT) {
            if (x - 1 >= 0 && this->garden->matrix[x - 1][y] == 0) {
                this->garden->matrix[x - 1][y] = this->garden->matrix[x][y] + 1;
                moveFarmer(x - 1, y, LEFT);
            } else if (y - 1 >= 0 && this->garden->matrix[x][y - 1] == 0) {
                this->garden->matrix[x][y - 1] = this->garden->matrix[x][y] + 1;
                moveFarmer(x, y - 1, LEFT);
            } else if (x + 1 < this->garden->rows && this->garden->matrix[x + 1][y] == 0) {
                this->garden->matrix[x + 1][y] = this->garden->matrix[x][y] + 1;
                moveFarmer(x + 1, y, LEFT);
            } else if (y + 1 < this->garden->columns && this->garden->matrix[x][y + 1] == 0) {
                this->garden->matrix[x][y + 1] = this->garden->matrix[x][y] + 1;
                moveFarmer(x, y + 1, LEFT);
            } else {
                // farmer is stuck
                return;
            }
        }
    }
};

class Generation{
public:
    int max_genes;
    int generation_number;
    int farmers_count;
    int matrix_rows;
    int matrix_columns;

    /*farmer number, fitness for that farmer*/
    vector<vector<int>> fitness_through_generations;
    vector<Farmer*> farmer;

    Generation *next;

    Generation(int farmers_count, int max_genes, int rows, int columns, int generation_number)
    {
        this->max_genes = max_genes;
        this->generation_number = generation_number;
        this->farmers_count = farmers_count;
        this->matrix_rows = rows;
        this->matrix_columns = columns;
        this->next = nullptr;

        for(int i=0; i<farmers_count; i++)
        {
            Farmer *f = new Farmer(this->max_genes, this->matrix_rows, this->matrix_columns, i);
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

        delete next;
        next = nullptr;
    }

        /*niekde treba mat isFinal, este neviem kde*/

//    static bool isFinal(Garden *g /*stones count*/)
//    {
//        int done = Farmer::fitnessFunction(g);
//
//        if(done == g->rows*g->columns /* minus stone count*/)
//        {
//            return true;
//        }
//        // add condition for when it is not possible to finish
//        else if()
//        {
//
//        }
//        else
//        {
//            return false;
//        }
//    }

};


#endif //UI_ZADANIE2A_GARDEN_H

#pragma clang diagnostic pop