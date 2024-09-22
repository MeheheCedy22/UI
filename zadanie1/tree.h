#ifndef UI_ZADANIE1_TREE_H
#define UI_ZADANIE1_TREE_H

#pragma once

#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>

#define N 9
#define MANHATTAN "manhattan"
#define MISPLACED "misplaced"


enum class direction{
    NONE = 0,
    UP,
    DOWN,
    LEFT,
    RIGHT
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

    Node(const int state[], int depth)
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

        this->dir = direction::NONE;
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

    static void printNode(const Node *node)
    {
        if(node == nullptr)
        {
            return;
        }
        std::cout << node->state[0] << " " << node->state[1] << " " << node->state[2] << "\n";
        std::cout << node->state[3] << " " << node->state[4] << " " << node->state[5] << "\n";
        std::cout << node->state[6] << " " << node->state[7] << " " << node->state[8] << "\n";
        std::cout << "\n";
    }
};

class Tree{
public:
    Node *root;
    std::vector<Node*> created;
    std::unordered_map<std::string, Node*> processed;

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

    static void printTree(Node *node)
    {
        std::cout << "Tree nodes (in reversed order / from end to start):\n!! END !!\n\n";
        std::cout << "  ^\n";
        std::cout << "  |\n\n";
        Node *current = node;
        while(current->prev != nullptr) {
            Node::printNode(current);
            std::cout << "  ^" << "\t" << dirToString(current->dir) << "\n";
            std::cout << "  |\n\n";
            current = current->prev;
        }
        Node::printNode(current);
        std::cout << "  ^\n";
        std::cout << "  |\n\n";
        std::cout << "!! START !!\n\n";
    }

    static std::string dirToString(direction dir)
    {
        switch(dir)
        {
            case direction::UP:
                return "UP";
            case direction::DOWN:
                return "DOWN";
            case direction::LEFT:
                return "LEFT";
            case direction::RIGHT:
                return "RIGHT";
            default:
                return "NONE";
        }
    }

    void generateStates(Node *node)
    {
        std::vector<direction> states = possibleStates(node);

        if(states[0] == direction::NONE)
        {
            return;
        }

        for(auto & state : states)
        {
            int new_state[N];
            for(int j=0;j<N;j++)
            {
                new_state[j] = node->state[j];
            }
            switch (state)
            {
                case direction::UP:
                    swap(new_state, getIndex(new_state, 0), getIndex(new_state, 0) - 3);
                    break;
                case direction::DOWN:
                    swap(new_state, getIndex(new_state, 0), getIndex(new_state, 0) + 3);
                    break;
                case direction::LEFT:
                    swap(new_state, getIndex(new_state, 0), getIndex(new_state, 0) - 1);
                    break;
                case direction::RIGHT:
                    swap(new_state, getIndex(new_state, 0), getIndex(new_state, 0) + 1);
                    break;
                default:
                    break;
            }


            if(processed.find(getStrRepresentation(new_state)) == processed.end()) // if the state is not in the map, then process it
            {
                Node *new_node = new Node(new_state, node->depth + 1);
                new_node->prev = node;
                new_node->dir = state;

                switch (state)
                {
                    case direction::UP:
                        node->up = new_node;
                        break;
                    case direction::DOWN:
                        node->down = new_node;
                        break;
                    case direction::LEFT:
                        node->left = new_node;
                        break;
                    case direction::RIGHT:
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

    static std::vector<direction> possibleStates(const Node *node)
    {
        int zero_index;
        if((zero_index = getIndex(node->state, 0)) == -1)
        {
            return {direction::NONE};
        }

        switch (zero_index)
        {
            case 0:
                return {direction::RIGHT, direction::DOWN};
            case 1:
                return {direction::LEFT, direction::RIGHT, direction::DOWN};
            case 2:
                return {direction::LEFT, direction::DOWN};
            case 3:
                return {direction::UP, direction::RIGHT, direction::DOWN};
            case 4:
                return {direction::UP, direction::LEFT, direction::RIGHT, direction::DOWN};
            case 5:
                return {direction::UP, direction::LEFT, direction::DOWN};
            case 6:
                return {direction::UP, direction::RIGHT};
            case 7:
                return {direction::UP, direction::LEFT, direction::RIGHT};
            case 8:
                return {direction::UP, direction::LEFT};
            default:
                return {direction::NONE};
        }
    }

    static bool checkFinal(const Node *node, const int goal[])
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


    static bool solvable(const int state[], const int goal[])
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
            int temp_index = getIndex(state, goal[i]);
            int x = temp_index % 3;
            int y = temp_index / 3;
            int x_goal = i % 3;
            int y_goal = i / 3;
            sum += abs(x - x_goal) + abs(y - y_goal);
        }
        return sum;
    }
    static int misplacedSquares(const int state[], const int goal[])
    {
        int sum = 0;
        for (int i = 0; i < N; i++)
        {
            if (state[i] != goal[i])
            {
                sum += 1;
            }
        }
        return sum;
    }

    static int applyHeuristic(const int state[], const int goal[], const std::string& heuristic) {
        if (heuristic == MANHATTAN)
        {
            return manhattanDistance(state, goal);
        }
        if (heuristic == MISPLACED)
        {
            return misplacedSquares(state, goal);
        }

        return -1;
    }

    static std::string getStrRepresentation(int arr[])
    {
        std::string str;
        for(int i=0;i<N;i++)
        {
            str += std::to_string(arr[i]);
        }
        return str;
    }
};
#endif //UI_ZADANIE1_TREE_H