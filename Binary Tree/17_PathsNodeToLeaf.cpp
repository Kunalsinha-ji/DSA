#include <bits/stdc++.h>
using namespace std;

/*

Definition for Binary Tree Node
struct Node
{
    int data;
    struct Node* left;
    struct Node* right;

    Node(int x){
        data = x;
        left = right = NULL;
    }
};
*/

class Solution {
    void solve(Node* &root,vector<vector<int>> &ans, vector<int> v){
        if(root==NULL){
            return;
        }
        if(root->left==NULL && root->right==NULL){
            v.push_back(root->data);
            ans.push_back(v);
            v.pop_back();
            return;
        }

        v.push_back(root->data);
        solve(root->left,ans,v);
        solve(root->right,ans,v);
        v.pop_back();
    }
  public:
    vector<vector<int>> Paths(Node* root) {
        // code here
        vector<vector<int>> ans;
        solve(root,ans,{});

        return ans;
    }
};

int main() {
    return 0;
}