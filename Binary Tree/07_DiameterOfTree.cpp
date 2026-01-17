#include <bits/stdc++.h>
using namespace std;

/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
 * };
 */
class Solution {
    pair<int,int> solve(TreeNode* &root){
        if(root==NULL){
            return {0,0};
        }

        pair<int,int> left = solve(root->left);
        pair<int,int> right = solve(root->right);

        int height = max(left.first,right.first) + 1;
        int diameter = max({left.second,right.second,(left.first+right.first+1)});

        return {height,diameter};
    }
public:
    int diameterOfBinaryTree(TreeNode* root) {
        return solve(root).second-1;
    }
};

int main() {
    return 0;
}