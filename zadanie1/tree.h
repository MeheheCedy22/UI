#ifndef UI_ZADANIE1_TREE_H
#define UI_ZADANIE1_TREE_H


#include <iostream>
#include <string>
#include <algorithm>
#include <vector>
#include <unordered_map>
#include <chrono>

#define N 9
#define MANHATTAN "manhattan"
#define MISPLACED "misplaced"

using namespace std::chrono;

using std::cin;
using std::cout;
using std::endl;
using std::string;



enum direction{
    UP,
    DOWN,
    LEFT,
    RIGHT,
    ERROR,
    NONE
};

class Node{
public:
    int state[N]{};
    int depth;
    direction dir; // what direction was used to get to this state

    Node *up;
    Node *down;
    Node *left;
    Node *right;
    Node *prev;

    Node(int state[], int depth)
    {
        for(int i=0;i<N;i++)
        {
            this->state[i] = state[i];
        }
        this->up = nullptr;
        this->down = nullptr;
        this->left = nullptr;
        this->right = nullptr;
        this->prev = nullptr;

        this->dir = NONE;
        this->depth = depth;
    }
    ~Node()
    {
        delete up;
        delete down;
        delete left;
        delete right;

        up = nullptr;
        down = nullptr;
        left = nullptr;
        right = nullptr;
    }
};

class Tree{
public:
    Node *root;
    std::vector<Node*> created;
    std::unordered_map<string, Node*> processed;

    Tree()
    {
        root = nullptr;
    }

    ~Tree()
    {
        if (root)
        {
            delete root;
            root = nullptr;
        }

    }

    void printNode(Node *node)
    {
        if(node == nullptr)
        {
            return;
        }
        cout << node->state[0] << " " << node->state[1] << " " << node->state[2] << endl;
        cout << node->state[3] << " " << node->state[4] << " " << node->state[5] << endl;
        cout << node->state[6] << " " << node->state[7] << " " << node->state[8] << endl;
        cout << endl;
    }

    void generateStates(Node *node)
    {
        std::vector<direction> states = possibleStates(node);

        if(states[0] == ERROR)
        {
            return;
        }

        for(int i=0;i<states.size();i++)
        {
            int new_state[N];
            for(int j=0;j<N;j++)
            {
                new_state[j] = node->state[j];
            }
            switch (states[i])
            {
                case UP:
                    swap(new_state, getIndex(new_state, 0), getIndex(new_state, 0) - 3);
                    break;
                case DOWN:
                    swap(new_state, getIndex(new_state, 0), getIndex(new_state, 0) + 3);
                    break;
                case LEFT:
                    swap(new_state, getIndex(new_state, 0), getIndex(new_state, 0) - 1);
                    break;
                case RIGHT:
                    swap(new_state, getIndex(new_state, 0), getIndex(new_state, 0) + 1);
                    break;
                default:
                    break;
            }


            if(processed.find(getStrRepresentation(new_state)) == processed.end()) // if the state is not in the map, then process it
            {
                Node *new_node = new Node(new_state, node->depth + 1);
                new_node->prev = node;
                new_node->dir = states[i];

                switch (states[i])
                {
                    case UP:
                        node->up = new_node;
                        break;
                    case DOWN:
                        node->down = new_node;
                        break;
                    case LEFT:
                        node->left = new_node;
                        break;
                    case RIGHT:
                        node->right = new_node;
                        break;
                    default:
                        break;
                }
                created.push_back(new_node);
                processed[getStrRepresentation(new_state)] = new_node;
            }
        }
    }


    static void swap(int state[], int index1, int index2)
    {
        int temp = state[index1];
        state[index1] = state[index2];
        state[index2] = temp;
    }

    std::vector<direction> possibleStates(Node *node)
    {
        int zero_index;
        if((zero_index = getIndex(node->state, 0)) == -1)
        {
            return {ERROR};
        }

        switch (zero_index)
        {
            case 0:
                return {RIGHT, DOWN};
            case 1:
                return {LEFT, RIGHT, DOWN};
            case 2:
                return {LEFT, DOWN};
            case 3:
                return {UP, RIGHT, DOWN};
            case 4:
                return {UP, LEFT, RIGHT, DOWN};
            case 5:
                return {UP, LEFT, DOWN};
            case 6:
                return {UP, RIGHT};
            case 7:
                return {UP, LEFT, RIGHT};
            case 8:
                return {UP, LEFT};
            default:
                return {ERROR};
        }
    }

    static bool checkFinal(Node *node, const int goal[])
    {
        for(int i=0;i<N;i++)
        {
            if(node->state[i] != goal[i])
            {
                return false;
            }
        }
        return true;
    }

    static int getIndex(const int state[], int value)
    {
        for(int i=0;i<N;i++)
        {
            if(state[i] == value)
            {
                return i;
            }
        }
        return -1;
    }


    static bool solvable(int state[], int goal[])
    {
        int sum_goal = 0;

        for(int i=0;i<N;i++)
        {
            if (state[i] == 0) continue;
            for(int j=i+1;j<N;j++)
            {
                if (state[j] == 0) continue;
                // this if-clause detects if the number is not in the array
                if(getIndex(goal, state[i]) == -1 || getIndex(goal, state[j]) == -1)
                {
                    return false;
                }

                if(getIndex(goal, state[i]) > getIndex(goal, state[j]))
                {
                    sum_goal++;
                }
            }
        }

        return !(sum_goal % 2);
    }

    static int manhattanDistance(const int state[], const int goal[])
    {
        int sum = 0;
        for(int i=0;i<N;i++)
        {
            int x = state[i] % 3;
            int y = state[i] / 3;
            int x_goal = goal[i] % 3;
            int y_goal = goal[i] / 3;
            sum += abs(x - x_goal) + abs(y - y_goal);
        }
        return sum;
    }
    static int misplacedSquares(const int state[], const int goal[]) {
        int sum = 0;
        for (int i = 0; i < N; i++) {
            if (state[i] != goal[i]) {
                sum += 1;
            }
        }
        return sum;
    }

    static int applyHeuristic(const int state[], const int goal[], string heuristic) {
        if (heuristic == MANHATTAN)
        {
            return manhattanDistance(state, goal);
        }
        else if (heuristic == MISPLACED)
        {
            return misplacedSquares(state, goal);
        }
        else
        {
            return -1;
        }
    }


    static string getStrRepresentation(int arr[])
    {
        string str;
        for(int i=0;i<N;i++)
        {
            str += std::to_string(arr[i]);
        }
        return str;
    }


};
#endif //UI_ZADANIE1_TREE_H