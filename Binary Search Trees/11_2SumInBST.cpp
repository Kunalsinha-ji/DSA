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
    void solve(TreeNode* &root,vector<int> &ans){
        if(root==NULL)  return;

        solve(root->left,ans);
        ans.push_back(root->val);
        solve(root->right,ans);
    }
public:
    bool findTarget(TreeNode* root, int k) {
        if(root==NULL)  return 0;

        vector<int> in;
        solve(root,in);

        if(in.size()==1){
            return 0;
        }

        int i=0,j=in.size()-1;
        while(i<j){
            if(in[i]+in[j]==k)  return 1;
            else if(in[i]+in[j]>k){
                j--;
            }
            else{
                i++;
            }
        }
        return 0;
    }
};

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
class Solution2 {
    bool solve(TreeNode* &root,int sum,unordered_map<int,int> &mp){
        if(root==NULL){
            return 0;
        }

        int data = root->val;
        if(mp.find(data)!=mp.end()) return 1;

        mp[sum-data] = 1;

        bool left = solve(root->left,sum,mp);
        bool right = solve(root->right,sum,mp);

        return left || right;
    }
public:
    bool findTarget(TreeNode* root, int k) {
        unordered_map<int,int> mp;
        return solve(root,k,mp);
    }
};

int main() {
    return 0;
}