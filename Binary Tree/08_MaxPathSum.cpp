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
    int solve(TreeNode* &root,int &ans){
        if(root==NULL){
            return 0;
        }

        int left = max(solve(root->left,ans),0);
        int right = max(solve(root->right,ans),0);

        ans = max(ans,max(max(left,right)+root->val,left+right+root->val));
        return max(left,right) + root->val;
    }
public:
    int maxPathSum(TreeNode* root) {
        int ans = INT_MIN;
        solve(root,ans);
        return ans;
    }
};

int main() {
    return 0;
}