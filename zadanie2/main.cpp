#pragma clang diagnostic push
#pragma ide diagnostic ignored "modernize-use-auto"
#include <iostream>
#include "garden.h"


// stones are represented as (-1)
// then printed as K
// use tournament selection, so take best 2-4 individuals and make the best one parent and then
// do cross-over and mutation with the other ones
// farmer are going straight until they hit an obstacle (stone or done path), then they go left or right
// farmer always wants to go to the right, if cant then left

void compute();

auto measureTime()
{
    auto start = high_resolution_clock::now();
    compute();
    auto end = high_resolution_clock::now();
    auto duration = duration_cast<microseconds>(end - start);

    return duration.count();
}


int main()
{
    compute();

//    auto timeTaken = measureTime();
//    cout << "Time taken: " << timeTaken << " microseconds" << endl;

    return 0;
}

void compute()
{
    int rows, columns, stones_count, max_genes, number_of_generations, number_of_farmers_in_generation;
    rows = columns = stones_count = max_genes = number_of_generations = number_of_farmers_in_generation = 0;

    // 2D vector to store stone positions
    vector<vector<int>> stones;

/*---------------------------------------------*/
    /* Manual input: */
//    cout << "Enter the number of rows in the matrix: ";
//    cin >> rows;
//    cout << "Enter the number of columns in the matrix: ";
//    cin >> columns;
//    cout << "Enter number of generations: ";
//    cin >> number_of_generations;
//    cout << "Enter number of farmers in generation: ";
//    cin >> number_of_farmers_in_generation;
//    cout << "Enter number of stones: ";
//    cin >> stones_count;
//
//    if (stones_count != 0)
//    {
//        cout << "Indexing start from 0" << endl;
//        cout << "Range: (0,0) " << "(" << rows-1 << "," << columns-1 << ")" << endl;
//    }
//
//    for(int i=0; i<stones_count; i++)
//    {
//        int x, y;
//        cout << "Enter the position of stone (x y) number " << i+1 << ": ";
//        cin >> x >> y;
//        stones.push_back({x, y});
//    }

    /* Automatic input as example from assignment: */
    rows = 10;
    columns = 12;
    stones_count = 6;
    number_of_generations = 5; //default 512
    number_of_farmers_in_generation = 3; //default 32
    stones.push_back({1, 5});
    stones.push_back({2, 1});
    stones.push_back({3, 4});
    stones.push_back({4, 2});
    stones.push_back({6, 8});
    stones.push_back({6, 9});
/*---------------------------------------------*/

    max_genes = rows+columns+stones_count;
    Generation *first_gen = new Generation(number_of_farmers_in_generation, max_genes, rows, columns, 0);
    Generation *current = first_gen;

    for(int i=0; i < number_of_generations; i++)
    {
        cout << "i: " << i << endl;
        for(int j=0; j < number_of_farmers_in_generation; j++)
        {
            current->farmer[j]->genes->randomGenerateGene();
            current->farmer[j]->garden->setStones(stones);
            // walkGarden
            current->farmer[j]->fitnessFunction();
            current->fitness_through_generations.push_back({j, current->farmer[j]->fitness});
            // selection
            // cross-over
            // mutation
            // repeat
            cout << "Generation: " << current->generation_number << " Farmer: " << current->farmer[j]->farmer_number << endl;
            current->farmer[j]->genes->printGenes();
            current->farmer[j]->garden->printGarden();
            cout << endl;
        }





        if(i != number_of_generations-1)
        {
            current->next = new Generation(number_of_farmers_in_generation, max_genes, rows, columns, i+1);
            current = current->next;
        }
    }

    /* Testing */
    cout << "last gen number: " << current->generation_number << endl;
    if(current->next== nullptr)
    {
        cout << "current->next is nullptr" << endl;
    }
    /*----------*/



    delete first_gen;
    first_gen = nullptr;
}

#pragma clang diagnostic pop