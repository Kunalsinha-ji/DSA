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
    TreeNode* solve(vector<int> &pre,vector<int> &in,int &i,int l,int r,unordered_map<int,int> &mp){
        if(l>r || i>=pre.size()){
            return NULL;
        }

        TreeNode* root = new TreeNode(pre[i]);
        int mid = mp[pre[i++]];
        root->left = solve(pre,in,i,l,mid-1,mp);
        root->right = solve(pre,in,i,mid+1,r,mp);

        return root;
    }
public:
    TreeNode* bstFromPreorder(vector<int>& preorder) {
        int n = preorder.size();
        vector<int> inorder = preorder;
        sort(inorder.begin(),inorder.end());

        unordered_map<int,int> mp;
        for(int i=0;i<n;i++){
            mp[inorder[i]] = i;
        }

        int ind = 0;
        return solve(preorder,inorder,ind,0,n-1,mp);
    }
};

int main() {
    return 0;
}