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
    TreeNode* solve(vector<int> &post,vector<int> &in,int &ind,int l,int r,unordered_map<int,int> &mp){
        if(l>r || ind<0){
            return NULL;
        }

        TreeNode* root = new TreeNode(post[ind]);
        int mid = mp[post[ind--]];
        root->right = solve(post,in,ind,mid+1,r,mp);
        root->left = solve(post,in,ind,l,mid-1,mp);
        return root;
    }
public:
    TreeNode* buildTree(vector<int>& inorder, vector<int>& postorder) {
        int n = postorder.size();
        unordered_map<int,int> mp;

        for(int i=0;i<n;i++){
            mp[inorder[i]] = i;
        }
        int ind = n-1;
        return solve(postorder,inorder,ind,0,n-1,mp);
    }
};

int main() {
    return 0;
}