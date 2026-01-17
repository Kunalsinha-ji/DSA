#include <bits/stdc++.h>
using namespace std;

/*
class Node {
  public:
    int data;
    Node* left;
    Node* right;

    // Constructor to initialize a new node
    Node(int val) {
        data = val;
        left = NULL;
        right = NULL;
    }
};
*/

class Solution {
    void solveLeft(Node* &root,vector<int> &ans){
        if(root==NULL){
            return;
        }
        if(root->left==NULL && root->right==NULL){
            return;
        }

        ans.push_back(root->data);

        if(root->left){
            solveLeft(root->left,ans);
        }
        else{
            solveLeft(root->right,ans);
        }
    }

    void solveRight(Node* &root,vector<int> &ans){
        if(root==NULL){
            return;
        }
        if(root->left==NULL && root->right==NULL){
            return;
        }

        if(root->right){
            solveRight(root->right,ans);
        }
        else{
            solveRight(root->left,ans);
        }
        ans.push_back(root->data);
    }

    void solveLeaf(Node* &root,vector<int> &ans){
        if(root==NULL){
            return;
        }
        if(root->left==NULL && root->right==NULL){
            ans.push_back(root->data);
            return;
        }

        solveLeaf(root->left,ans);
        solveLeaf(root->right,ans);
    }
  public:
    vector<int> boundaryTraversal(Node *root) {
        // code here
        vector<int> ans;
        ans.push_back(root->data);
        if(root->left==NULL && root->right==NULL){
            return ans;
        }
        solveLeft(root->left,ans);
        solveLeaf(root,ans);
        solveRight(root->right,ans);

        return ans;
    }
};

int main() {
    return 0;
}