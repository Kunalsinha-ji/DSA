#include <bits/stdc++.h>
using namespace std;

/*

class Node {
public:
    int data;
    Node* left;
    Node* right;

    Node(int val) {
        data = val;
        left = nullptr;
        right = nullptr;
    }
};

*/

class Solution {
    pair<bool,int > solve(Node* &root){
        if(root==NULL){
            return {1,0};
        }
        if(root->left==NULL && root->right==NULL){
            return {1,root->data};
        }

        pair<bool,int> left = solve(root->left);
        pair<bool,int> right = solve(root->right);

        if(left.first==0 || right.first==0)   return {0,0};
        else if(left.second + right.second != root->data)   return {0,0};
        else{
            return {1,root->data};
        }
    }
  public:
    bool isSumProperty(Node *root) {
        return solve(root).first;
    }
};

int main() {
    return 0;
}