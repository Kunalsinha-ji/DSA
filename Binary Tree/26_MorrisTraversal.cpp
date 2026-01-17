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
public:
    // Morris Traversal - Inorder
    vector<int> inorderTraversal(TreeNode* root) {
        vector<int> ans;

        while(root){
            if(root->left==NULL){
                ans.push_back(root->val);
                root=root->right;
            }
            else{
                TreeNode* curr = root->left;

                while(curr->right && curr->right!=root){
                    curr = curr->right;
                }
                // left is not traversed
                if(curr->right==NULL){
                    curr->right = root;
                    root = root->left;
                }
                // left is traversed
                else{
                    curr->right = NULL;
                    ans.push_back(root->val);
                    root=root->right;
                }
            }
        }
        return ans;
    }

    // Morris Traversal - Preorder
    vector<int> preorderTraversal(TreeNode* root) {
        vector<int> ans;

        while(root){
            if(root->left==NULL){
                ans.push_back(root->val);
                root = root->right;
            }
            else{
                TreeNode* curr = root->left;
                while(curr->right && curr->right!=root){
                    curr = curr->right;
                }

                // left is not traversed
                if(curr->right==NULL){
                    ans.push_back(root->val);
                    curr->right = root;
                    root = root->left;
                }
                // left is traversed
                else{
                    curr->right = NULL;
                    root = root->right;
                }
            }
        }
        return ans;
    }

    // Morris Traversal - Postorder
    // For this we need to perform mirror of preorder and at last reverse the array.
    // Mirror means: left <-> right && right <-> left
    vector<int> postorderTraversal(TreeNode* root) {
        vector<int> ans;

        while(root){
            if(root->right==NULL){
                ans.push_back(root->val);
                root = root->left;
            }
            else{
                TreeNode* curr = root->right;
                while(curr->left && curr->left!=root){
                    curr = curr->left;
                }

                // right is not traversed
                if(curr->left==NULL){
                    ans.push_back(root->val);
                    curr->left = root;
                    root = root->right;
                }
                // right is traversed
                else{
                    curr->left = NULL;
                    root = root->left;
                }
            }
        }
        reverse(ans.begin(),ans.end());
        return ans;
    }
};

int main() {
    return 0;
}