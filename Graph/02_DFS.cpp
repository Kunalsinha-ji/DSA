#include <bits/stdc++.h>
using namespace std;

class Solution {
    void dfs(int node,vector<int> &vis,vector<int> &ans,vector<vector<int>>& adj){
        vis[node] = 1;

        ans.push_back(node);

        for(auto it: adj[node]){
            if(!vis[it]){
                dfs(it,vis,ans,adj);
            }
        }
    }
  public:
    vector<int> dfs(vector<vector<int>>& adj) {
        int n = adj.size();

        vector<int> ans;
        vector<int> vis(n,0);

        dfs(0,vis,ans,adj);
        return ans;
    }
};\

int main() {
    return 0;
}