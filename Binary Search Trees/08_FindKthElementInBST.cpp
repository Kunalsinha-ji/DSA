#include <bits/stdc++.h>
using namespace std;

class Solution {
    void inorder(TreeNode* &root,vector<int> &v){
        if(root==NULL)  return;

        inorder(root->left,v);
        v.push_back(root->val);
        inorder(root->right,v);
    }
public:
    int kthSmallest(TreeNode* root, int k) {
        vector<int> v;

        inorder(root,v);

        return v[k-1];
    }

    // Optimized Approach
    int kthSmallestOptimized(TreeNode* root, int k) {
        stack<TreeNode*> st;
        TreeNode* curr = root;
        int count = 0;

        while(curr != NULL || !st.empty()){
            while(curr != NULL){
                st.push(curr);
                curr = curr->left;
            }

            curr = st.top();
            st.pop();
            count++;

            if(count == k)
                return curr->val;

            curr = curr->right;
        }
        return -1; // This line should never be reached if k is valid
    }
};

int main() {
    return 0;
}