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
    bool solve(TreeNode* &root, int leftLimit, int rightLimit){
        if(root==NULL){
            return 1;
        }
        if(root->val<=leftLimit || root->val>=rightLimit){
            return 0;
        }

        bool left = solve(root->left,leftLimit,root->val);
        bool right = solve(root->right,root->val,rightLimit);

        return left && right;
    }
public:
    bool isValidBST(TreeNode* root) {
        return solve(root,INT_MIN,INT_MAX);
    }
};

int main() {
    return 0;
}