#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    TreeNode* deleteNode(TreeNode* root, int key) {
        if (!root) return NULL;

        if (key < root->val) {
            root->left = deleteNode(root->left, key);
        }
        else if (key > root->val) {
            root->right = deleteNode(root->right, key);
        }
        else {
            // Node found
            if (!root->left) {
                TreeNode* temp = root->right;
                delete root;
                return temp;
            }
            else if (!root->right) {
                TreeNode* temp = root->left;
                delete root;
                return temp;
            }
            else {
                // Find inorder successor
                TreeNode* succ = root->right;
                while (succ->left) {
                    succ = succ->left;
                }
                root->val = succ->val;
                root->right = deleteNode(root->right, succ->val);
            }
        }
        return root;
    }
};


int main() {
    return 0;
}