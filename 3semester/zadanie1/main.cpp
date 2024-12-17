#include <iostream>
#include <string>
#include <chrono>
#include "tree.h"

#define N 9
#define MANHATTAN "manhattan"
#define MISPLACED "misplaced"
#define MANUAL 0
#define DEBUG_PRINT 0

// init state examples

//  1   {6, 2, 0, 1, 5, 3, 4, 7, 8};
//  2   {1, 2, 3, 4, 6, 8, 7, 5, 0};
//  3   {7, 3, 5, 2, 4, 1, 8, 6, 0};
//  4   {2, 3, 8, 7, 1, 5, 0, 4, 6};
//  5   {2, 4, 3, 1, 6, 8, 0, 7, 5};
//  6   {4, 1, 6, 7, 3, 2, 0, 5, 8};
//  7   {1, 2, 3, 7, 4, 8, 0, 6, 5};
//  8   {1, 3, 0, 4, 2, 8, 7, 6, 5};
//  9   {1, 2, 3, 8, 0, 5, 4, 7, 6};
//  10  {4, 2, 3, 7, 1, 8, 5, 6, 0};

//  11  {1, 3, 5, 4, 8, 2, 7, 6, 0};
//  12  {1, 7, 2, 5, 0, 3, 6, 4, 8};
//  13  {0, 1, 3, 4, 2, 5, 7, 8, 6};
//  14  {4, 1, 2, 7, 0, 3, 6, 8, 5};
//  15  {4, 2, 3, 5, 1, 6, 0, 7, 8};
//  16  {4, 1, 3, 2, 0, 6, 7, 5, 8};
//  17  {0, 2, 6, 1, 3, 8, 7, 4, 5};
//  18  {1, 3, 6, 2, 0, 4, 7, 8, 5};
//  19  {2, 3, 5, 7, 1, 4, 0, 8, 6};
//  20  {3, 6, 8, 1, 0, 2, 5, 4, 7};

// goal state example

//      {1, 2, 3, 4, 5, 6, 7, 8, 0};


// in my implemenation the blank space is represented by number 0
// in my implementation, i move the blank space instead of the given number with the operators

void compute(const std::string &heuristic_pass) {

# if MANUAL
    int state[N]{};
    int goal[N]{};

    std::cout << "\nMatrix 3x3:\n";
    std::cout << "Number '0' represents the blank space\n";
    std::cout << "Example:\n";
    std::cout << "1 2 3\n";
    std::cout << "4 5 6\n";
    std::cout << "7 8 0\n";
    std::cout << "\nEnter the initial state of the puzzle:\n";
    for(int & i : state)
    {
        std::cin >> i;
    }

    std::cout << "Enter the goal state of the puzzle:\n";
    for(int & i : goal)
    {
        std::cin >> i;
    }

    std::cout << "\n";
#else

    const int state[N] = {3, 4, 6, 1, 0, 2, 7, 5, 8};
    const int goal[N] = {1,2,3,4,5,6,7,8,0};

#endif

    Tree tree;
    tree.root = new Node(state, 0);
    Node *current = tree.root;
    Node *final = nullptr;
    std::string final_path;


    if(Tree::checkFinal(current, goal))
    {
        std::cout << "The puzzle is already solved\n";
        return;
    }

    if(!(Tree::solvable(state, goal)))
    {
        std::cout << "The puzzle is not solvable\n";
        return;
    }

    tree.created.push_back(tree.root);

    while(true)
    {
        int temp_heuristic=Tree::applyHeuristic(tree.created[0]->state, goal, heuristic_pass);
        int temp_index=0;

        for(int i=0; i< tree.created.size(); i++)
        {
            int inHeuristic = Tree::applyHeuristic(tree.created[i]->state, goal, heuristic_pass);
            if(inHeuristic < temp_heuristic)
            {
                temp_heuristic = inHeuristic;
                temp_index = i;
            }
        }

        current = tree.created[temp_index];

        if(Tree::checkFinal(current, goal))
        {
            final = current;
            break;
        }

        tree.generateStates(current);

        // remove the node (one element from created vector) at the temp_index
        tree.created.erase(tree.created.begin() + temp_index, tree.created.begin() + temp_index + 1);
    }
    std::cout << "\n\n";




    int steps = final->depth;
    Node *temp = final;
    // backtracking of the taken steps
    while(temp->prev != nullptr)
    {
        final_path += Tree::dirToString(temp->dir) + " <- ";
        temp = temp->prev;
    }

    final_path += "!! START !!";

    Tree::printTree(final);
    std::cout << "Steps: " << steps << "\n";
    std::cout << "Path: " << final_path << "\n\n";
    std::cout << "Initial:\n";
    Node::printNode(tree.root);
    std::cout<< "Final:\n";
    Node::printNode(final);
    std::cout << "--------------------------------------\n";
}

auto timeMeasure(const std::string &heuristic_pass)
{
    auto start = std::chrono::high_resolution_clock::now();
    compute(heuristic_pass);
    auto end = std::chrono::high_resolution_clock::now();
    return std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();
}


int main() {

    // TODO implement a way to count the number of explored nodes
    // TODO learn the logic behind created and processsed vecotr and hash map respectively
    // static unsigned int exploredNodeCount = 0;

#if MANUAL
    std::cout << "\n\n--------------Misplaced heuristic--------------\n";
    compute(MISPLACED);
    std::cout << "\n\n";
    std::cout << "\n\n--------------Manhattan heuristic--------------\n";
    compute(MANHATTAN);
    std::cout << "\n\n";
#else

    auto duration_miss = timeMeasure(MISPLACED);
    auto duration_manh = timeMeasure(MANHATTAN);

    std::cout << "Time for Misplaced: " << duration_miss << " microseconds\n";
    std::cout << "Time for Manhattan: " << duration_manh << " microseconds\n";
#endif

    return 0;
}