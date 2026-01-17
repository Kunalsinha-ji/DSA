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
    TreeNode* solve(vector<int> &pre,vector<int> &in,int &ind,int l,int r,unordered_map<int,int> &mp){
        if(l>r || ind>=in.size()){
            return NULL;
        }

        TreeNode* root = new TreeNode(pre[ind]);
        int mid = mp[pre[ind++]];
        root->left = solve(pre,in,ind,l,mid-1,mp);
        root->right = solve(pre,in,ind,mid+1,r,mp);
        return root;
    }
public:
    TreeNode* buildTree(vector<int>& preorder, vector<int>& inorder) {
        unordered_map<int,int> mp;
        for(int i=0;i<inorder.size();i++){
            mp[inorder[i]] = i;
        }
        int ind = 0;
        return solve(preorder,inorder,ind,0,inorder.size()-1,mp);
    }
};

int main() {
    return 0;
}