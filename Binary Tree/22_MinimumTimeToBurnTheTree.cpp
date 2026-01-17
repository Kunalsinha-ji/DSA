#include <bits/stdc++.h>
using namespace std;

/*
class Node {
  public:
    int data;
    Node *left;
    Node *right;

    Node(int val) {
        data = val;
        left = right = NULL;
    }
};
*/

class Solution {
    void getAdj(unordered_map<int,vector<int>> &adj, Node* &root){
        if(root==NULL){
            return;
        }

        if(root->left){
            Node* leftChild = root->left;
            adj[root->data].push_back(leftChild->data);
            adj[leftChild->data].push_back(root->data);
            getAdj(adj,leftChild);
        }
        if(root->right){
            Node* rightChild = root->right;
            adj[root->data].push_back(rightChild->data);
            adj[rightChild->data].push_back(root->data);
            getAdj(adj,rightChild);
        }
    }
  public:
    int minTime(Node* root, int target) {
        // code here
        unordered_map<int,vector<int>> adj;
        getAdj(adj,root);
        unordered_map<int,bool> vis;

        queue<pair<int,int>> q;
        q.push({target,0});
        vis[target] = 1;
        int ans = 0;

        while(!q.empty()){
            int node = q.front().first;
            int time = q.front().second;
            ans = max(ans,time);
            q.pop();

            for(auto i : adj[node]){
                if(!vis[i]){
                    q.push({i,time+1});
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