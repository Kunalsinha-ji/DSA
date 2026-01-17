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
    int inorder(TreeNode* &root){
        if(root==NULL){
            return 0;
        }
        int left = inorder(root->left);
        int right = inorder(root->right);
        return 1 + left + right;
    }
public:
    int countNodes(TreeNode* root) {
        return inorder(root);
    }
};

int main() {
    return 0;
}