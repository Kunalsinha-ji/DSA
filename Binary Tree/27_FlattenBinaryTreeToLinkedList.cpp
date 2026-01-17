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
    void flatten(TreeNode* root) {
        TreeNode* node = root;

        while(node){
            if(node->left==NULL){
                node = node->right;
            }
            else{
                TreeNode* curr = node->left;

                while(curr->right && curr->right!=node){
                    curr = curr->right;
                }

                // if left part is not traversed: not flattened
                if(curr->right==NULL){
                    curr->right = node;
                    node = node->left;
                }
                // if left part is traversed: flattened
                else{
                    TreeNode* p1 = node->left;
                    curr->right = node->right;
                    node->left = NULL;
                    node->right = p1;
                }
            }
        }
    }
};

int main() {
    return 0;
}