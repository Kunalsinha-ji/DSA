#include <bits/stdc++.h>
using namespace std;

/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode(int x) : val(x), left(NULL), right(NULL) {}
 * };
 */
class Solution {
    void getAdj(unordered_map<int,vector<int>> &adj, TreeNode* &root){
        if(root==NULL){
            return;
        }

        if(root->left){
            TreeNode* leftChild = root->left;
            adj[root->val].push_back(leftChild->val);
            adj[leftChild->val].push_back(root->val);
            getAdj(adj,leftChild);
        }
        if(root->right){
            TreeNode* rightChild = root->right;
            adj[root->val].push_back(rightChild->val);
            adj[rightChild->val].push_back(root->val);
            getAdj(adj,rightChild);
        }
    }
public:
    vector<int> distanceK(TreeNode* root, TreeNode* target, int k) {
        vector<int> ans;
        unordered_map<int,vector<int>> adj;
        unordered_map<int,bool> vis;

        getAdj(adj,root);

        queue<pair<int,int>> q;
        q.push({target->val,0});
        vis[target->val] = 1;

        while(!q.empty()){
            int node = q.front().first;
            int dist = q.front().second;
            q.pop();

            if(dist==k){
                ans.push_back(node);
                continue;
            }
            for(auto i : adj[node]){
                if(!vis[i]){
                    q.push({i,dist+1});
                    vis[i] = 1;
                }
            }
        }
        return ans;
    }
};

int main() {
    return 0;
}