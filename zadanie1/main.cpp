#include <iostream>
#include "tree.h"

//init state examples

//    {6, 2, 0, 1, 5, 3, 4, 7, 8};
//    {1, 2, 3, 4, 6, 8, 7, 5, 0};
//    {7, 3, 5, 2, 4, 1, 8, 6, 0};
//    {2, 3, 8, 7, 1, 5, 0, 4, 6};
//    {2, 4, 3, 1, 6, 8, 0, 7, 5};
//    {4, 1, 6, 7, 3, 2, 0, 5, 8};
//    {1, 2, 3, 7, 4, 8, 0, 6, 5};
//    {1, 3, 0, 4, 2, 8, 7, 6, 5};
//    {1, 2, 3, 8, 0, 5, 4, 7, 6};
//    {4, 2, 3, 7, 1, 8, 5, 6, 0};

//    {1, 3, 5, 4, 8, 2, 7, 6, 0};
//    {1, 7, 2, 5, 0, 3, 6, 4, 8};
//    {0, 1, 3, 4, 2, 5, 7, 8, 6};
//    {4, 1, 2, 7, 0, 3, 6, 8, 5};
//    {4, 2, 3, 5, 1, 6, 0, 7, 8};
//    {4, 1, 3, 2, 0, 6, 7, 5, 8};
//    {0, 2, 6, 1, 3, 8, 7, 4, 5};
//    {1, 3, 6, 2, 0, 4, 7, 8, 5};
//    {2, 3, 5, 7, 1, 4, 0, 8, 6};
//    {3, 6, 8, 1, 0, 2, 5, 4, 7};

//goal state

//    {1, 2, 3, 4, 5, 6, 7, 8, 0};

void compute(string heuristic_pass)
{
    // manual input

//    int state[N]{};
//    int goal[N]{};
//
//    cout << "Matrix 3x3: " << endl;
//    cout << "Number '0' represents the blank space" << endl;
//    cout << "Enter the initial state of the puzzle" << endl;
//    for(int i=0;i<N;i++)
//    {
//        cin >> state[i];
//    }
//
//    cout << "Enter the goal state of the puzzle" << endl;
//    for(int i=0;i<N;i++)
//    {
//        cin >> goal[i];
//    }
    // -----------------------------

    // faster testing input

    int state[N] = {1, 3, 6, 2, 0, 4, 7, 8, 5};
    int goal[N] = {1,2,3,4,5,6,7,8,0};
    // -----------------------------
    
    Tree *tree = new Tree();
    tree->root = new Node(state, 0);
    Node *current = tree->root;
    Node *final = nullptr;
    int steps = 0;
    string current_dir = "";
    string final_path = "";
    
    
    if(Tree::checkFinal(current, goal))
    {
        cout << "The puzzle is already solved" << endl;

        delete tree;
        return;
    }

    if(!(Tree::solvable(state, goal)))
    {
        cout << "The puzzle is not solvable" << endl;

        delete tree;
        return;
    }

    tree->created.push_back(tree->root);

    while(true)
    {
        int temp_heuristic=Tree::applyHeuristic(tree->created[0]->state, goal, heuristic_pass);
        int temp_index=0;
        
        for(int i=0; i< tree->created.size(); i++)
        {
            if(Tree::applyHeuristic(tree->created[i]->state, goal, heuristic_pass) < temp_heuristic)
            {
                temp_heuristic = Tree::applyHeuristic(tree->created[i]->state, goal, heuristic_pass);
                temp_index = i;
            }
        }
        
        current = tree->created[temp_index];
        
        if(Tree::checkFinal(current, goal))
        {
            final = current;
            break;
        }

        tree->generateStates(current);
        tree->created.erase(tree->created.begin() + temp_index, tree->created.begin() + temp_index + 1);
        // tree->printNode(current);
    }

    cout << endl << endl;

    cout << "Initial: "<<endl;
    tree->printNode(tree->root);
    cout<< "Final: "<<endl;
    tree->printNode(final);

    //backtracking of the taken steps

    while(final->prev != nullptr)
    {
        steps++;
        switch(final->dir)
        {
            case UP:
                current_dir = "UP";
                break;
            case DOWN:
                current_dir = "DOWN";
                break;
            case LEFT:
                current_dir = "LEFT";
                break;
            case RIGHT:
                current_dir = "RIGHT";
                break;
            case ERROR:
                current_dir = "ERROR";
                break;
            default:
                current_dir = "NONE";
                break;
        }
        final_path = final_path + current_dir + " <- ";
        final = final->prev;
    }

    final_path = final_path + "!! START !!";

    cout << "Steps: " << steps << endl;
    cout << "Path: " << final_path << endl;


    delete tree;

}

auto timeMeasure(string heuristic_pass)
{
    auto start = std::chrono::high_resolution_clock::now();
    compute(heuristic_pass);
    auto end = std::chrono::high_resolution_clock::now();
    return std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();
}


int main() {

    compute(MISPLACED);
    compute(MANHATTAN);

    auto duration_miss = timeMeasure(MISPLACED);
    auto duration_manh = timeMeasure(MANHATTAN);

    cout << "Time for Misplaced: " << duration_miss << " microseconds" << endl;
    cout << "Time for Manhattan: " << duration_manh << " microseconds" << endl;

    return 0;
}