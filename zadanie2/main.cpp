#include <iostream>
#include "garden.h"


// stones are represented as (-1)
// then printed as K
// use tournament selection, so take best 2-4 individuals and make the best one parent and then
// do cross-over and mutation with the other ones
// farmer are going straight until they hit an obstacle (stone or done path), then they go left or right
// farmer always wants to go to the right, if cant then left

bool compute();


int main()
{
    bool result = compute();

    if(result)
    {
        cout << "Found solution" << '\n';
    }
    else
    {
        cout << "Did not find solution" << '\n';
    }

    return 0;
}

bool compute()
{
    int rows, columns, stones_count, max_genes, number_of_generations, number_of_farmers_in_generation;
    rows = columns = stones_count = max_genes = number_of_generations = number_of_farmers_in_generation = 0;

    // 2D vector to store stone positions
    vector<vector<int>> stones;
    vector<Generation*> generations;

    int choice;
    cout << "Enter 0 for automatic input or 1 for manual input: ";
    cin >> choice;

    int print_min_max_avg;
    cout << "If you wish to print min, max, average enter 1, else 0: ";
    cin >> print_min_max_avg;
    cout << "\n";

    if(choice == 0)
    {
        rows = 10;
        columns = 12;
        stones_count = 6;
        number_of_generations = 256; //default 256
        number_of_farmers_in_generation = 128; //default 128, MUST BE EVEN NUMBER AND MUST BE GREATER OR EQUAL THAN 8
        stones.push_back({1, 5});
        stones.push_back({2, 1});
        stones.push_back({3, 4});
        stones.push_back({4, 2});
        stones.push_back({6, 8});
        stones.push_back({6, 9});
    }
    else if(choice == 1)
    {
        cout << "Enter the number of rows in the matrix: ";
        cin >> rows;
        cout << "Enter the number of columns in the matrix: ";
        cin >> columns;
        cout << "Enter number of generations (recommended 128-256): ";
        cin >> number_of_generations;
        cout << "Enter number of farmers in generation (MUST BE EVEN NUMBER, i.e. 128): ";
        cin >> number_of_farmers_in_generation;
        cout << "Enter number of stones (at least 1): ";
        cin >> stones_count;

        if (stones_count > 0)
        {
            cout << "Indexing start from 0" << '\n';
            cout << "Possible stone positions (from assignment):\n";
            cout << "1 5\n";
            cout << "2 1\n";
            cout << "3 4\n";
            cout << "4 2\n";
            cout << "6 8\n";
            cout << "6 9\n";
            cout << "Range: (0,0) " << "(" << rows-1 << "," << columns-1 << ")" << '\n';
        }

        for(int i=0; i < stones_count; i++)
        {
            int x, y;
            cout << "Enter the position of stone (x y) number " << i + 1 << ": ";
            cin >> x >> y;
            stones.push_back({x, y});
        }
    }
    else
    {
        cout << "Wrong input" << '\n';
        return false;
    }

    max_genes = rows+columns;
    Generation *generation = new Generation(number_of_farmers_in_generation, max_genes, stones_count, rows, columns, 0);
    generations.push_back(generation);

    for(int i=0; i < number_of_generations; i++)
    {
/*testing*/
//        cout << "number of generations, i: " << i << '\n';
/*--------------*/
        for(int j=0; j < number_of_farmers_in_generation; j++)
        {
            if(i==0)
            {
                generations[i]->farmer[j]->genes->randomGenerateGene();
/*testing*/
//                generations[i]->farmer[j]->genes->genes_vector = {{0,8}, {1,11}, {7,0}, {3,0}, {0,1}, {1,0}, {5,0}, {9,6}, {9,10}, {9,1}, {3,11}, {0,5}, {0,11}, {8,11}, {5,11}, {9,4}, {0,2}, {8,0}, {9,7}, {9,5}, {0,0}, {4,0}};
//                generations[i]->farmer[j]->genes->turn_genes = {-1, 1, -1, 1, 1, -1};
/*--------------*/
            }
            else
            {
                // uses sorted vector of fitnesses to select parents from previous generation

                // selection
                unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();
                srand(seed);
                unsigned int coinFlip = rand() % 2;
                vector<unsigned int> indexes;

                // uses already sorted vector of integers
                // gets indexes of half of the farmers in previous generation
                // then uses those indexes to get the genes of those farmers
                // then crossover
                if(coinFlip)
                {
                    // roulette selection
                    indexes = generations[i]->farmer[j]->rouletteSelection(generations[i-1]->fitness_through_generations);
/*testing*/
//                    cout << "using roulette selection\n";
/*--------------*/
                }
                else
                {
                    // fitness order selection
                    indexes = generations[i]->farmer[j]->fitnessOrder(generations[i-1]->fitness_through_generations);
/*testing*/
//                    cout << "using fitness order selection\n";
/*--------------*/
                }

                // cross-over
                // create new genes for farmer
                // new genes will be created as first half from one parent and second half from the other
                // then mutation

                // first parent, second is first + 1
                for (int k = 0; k < indexes.size(); k++)
                {
                    // for last iteration to now overflow
                    int x = k + 1;
                    if(k == indexes.size() - 1)
                    {
                        x = 0;
                    }
/*testing*/
//                    cout << "first for for crossover\n";
//                    cout <<"i: " << i << '\n';
//                    cout << "k: " << k << '\n';
//                    cout << "indexes[k]: " << indexes[k] << '\n';
//                    cout << "indexes[x]: " << indexes[x] << '\n';
//                    cout << "------------\n";
/*--------------*/
                    generations[i]->farmer[k]->genes->genes_vector.assign(
                            generations[i - 1]->farmer[indexes[k]]->genes->genes_vector.begin(),
                            generations[i - 1]->farmer[indexes[k]]->genes->genes_vector.begin() + max_genes / 2
                    );
                    generations[i]->farmer[k]->genes->genes_vector.insert(
                            generations[i]->farmer[k]->genes->genes_vector.end(),
                            generations[i - 1]->farmer[indexes[x]]->genes->genes_vector.begin() + max_genes / 2,
                            generations[i - 1]->farmer[indexes[x]]->genes->genes_vector.end()
                    );
                }

                // first parent, second is first + 2
                for (int k = 0; k < indexes.size(); k++)
                {
                    int x = k + 2;
                    if(k == indexes.size() - 2)
                    {
                        x = 0;
                    }
                    else if(k == indexes.size() - 1)
                    {
                        x = 1;
                    }
/*testing*/
//                    cout << "2nd for for crossover\n";
//                    cout <<"i: " << i << '\n';
//                    cout << "k: " << k << '\n';
//                    cout << "indexes[k]: " << indexes[k] << '\n';
//                    cout << "indexes[x]: " << indexes[x] << '\n';
//                    cout << "------------\n";
/*--------------*/
                    generations[i]->farmer[k + indexes.size()]->genes->genes_vector.assign(
                            generations[i - 1]->farmer[indexes[k]]->genes->genes_vector.begin(),
                            generations[i - 1]->farmer[indexes[k]]->genes->genes_vector.begin() + max_genes / 2
                    );
                    generations[i]->farmer[k + indexes.size()]->genes->genes_vector.insert(
                            generations[i]->farmer[k + indexes.size()]->genes->genes_vector.end(),
                            generations[i - 1]->farmer[indexes[x]]->genes->genes_vector.begin() + max_genes / 2,
                            generations[i - 1]->farmer[indexes[x]]->genes->genes_vector.end()
                    );
                }


                // for turn genes copy from first parent
                for (int o = 0; o < stones_count; o++) {
                    generations[i]->farmer[j]->genes->turn_genes.push_back(
                            generations[i - 1]->farmer[indexes[0]]->genes->turn_genes[o]
                    );
                }

                // mutation (porbability is done in teh function)
                generations[i]->farmer[j]->mutateGene();
/*testing*/
                // random generating only for testing now
                // generations[i]->farmer[j]->genes->randomGenerateGene();
/*--------------*/
            }

            generations[i]->farmer[j]->garden->setStones(stones);
            generations[i]->farmer[j]->walkGarden();
            generations[i]->farmer[j]->fitnessFunction();
            generations[i]->fitness_through_generations.push_back({j, generations[i]->farmer[j]->fitness});
/*testing*/
//            cout << "Generation: " << generations[i]->generation_number << " Farmer: " << generations[i]->farmer[j]->farmer_number << " Fitness: " << generations[i]->farmer[j]->fitness << '\n';
//            generations[i]->farmer[j]->genes->printGenes();
//            generations[i]->farmer[j]->garden->printGarden();
//            cout << '\n';
//
//          // show best possible solution even when none is found
//            if(generations[i]->farmer[j]->fitness >= 112)
//            {
//                cout << "Generation: " << generations[i]->generation_number << " Farmer: " << generations[i]->farmer[j]->farmer_number << " Fitness: " << generations[i]->farmer[j]->fitness <<'\n';
//                generations[i]->farmer[j]->genes->printGenes();
//                generations[i]->farmer[j]->garden->printGarden();
//            }
/*--------------*/

            if(generations[i]->farmer[j]->isFinal())
            {
                cout << "Solution: \n";
                cout << "Generation: " << generations[i]->generation_number << " Farmer: " << generations[i]->farmer[j]->farmer_number << '\n';
                generations[i]->farmer[j]->genes->printGenes();
                generations[i]->farmer[j]->garden->printGarden();
                cout << '\n';

                for(int x=0; x < generations.size(); x++)
                {
                    delete generations[x];
                }

                return true;
            }
        }

        // print data for fitness graph
        if(print_min_max_avg)
        {
            int max, min, average, sum;

            sum = average = 0;
            max = generations[i]->fitness_through_generations[0][1];
            min = generations[i]->fitness_through_generations[0][1];

            for(int y = 0; y < generations[i]->fitness_through_generations.size(); y++)
            {

                if(generations[i]->fitness_through_generations[y][1] > max)
                {
                    max = generations[i]->fitness_through_generations[y][1];
                }
                else if(generations[i]->fitness_through_generations[y][1] < min)
                {
                    min = generations[i]->fitness_through_generations[y][1];
                }

                sum += generations[i]->fitness_through_generations[y][1];
            }

            average = sum / generations[i]->fitness_through_generations.size();


            cout << generations[i]->generation_number << '\t' << min << '\t' << max << '\t' << average << '\n';
        }

        // sort farmers by fitness in descending order in the vector in generation
        sort(generations[i]->fitness_through_generations.begin(), generations[i]->fitness_through_generations.end(), [](const vector<int> &a, const vector<int> &b) {return a[1] > b[1];});

        if(i != number_of_generations-1)
        {
            Generation *next_generation = new Generation(number_of_farmers_in_generation, max_genes, stones_count, rows, columns, i+1);
            generations.push_back(next_generation);
        }
    }

    for(int i=0; i < number_of_generations; i++)
    {
        delete generations[i];
    }

    return false;
}