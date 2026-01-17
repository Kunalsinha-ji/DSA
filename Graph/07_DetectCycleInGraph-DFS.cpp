#include <bits/stdc++.h>
using namespace std;

class Solution {
    bool dfs(int node,vector<int> &vis,vector<int> adj[],int parent){
        vis[node] = 1;

        for(auto i: adj[node]){
            if(!vis[i]){
                bool res = dfs(i,vis,adj,node);
                if(res) return 1;
            }
            else if(i!=parent){
                return 1;
            }
        }
        return 0;
    }
  public:
    bool isCycle(int V, vector<vector<int>>& edges) {
        // Code here
        vector<int> vis(V,0);
        vector<int> adj[V];

        for(auto i: edges){
            int u = i[0];
            int v = i[1];

            adj[u].push_back(v);
            adj[v].push_back(u);
        }

        for(int i=0;i<V;i++){
            if(!vis[i]){
                bool isCycle = dfs(i,vis,adj,-1); // here -1 acts as parent node
                if(isCycle) return 1;
            }
        }
        return 0;
    }
};

int main() {
    return 0;
}