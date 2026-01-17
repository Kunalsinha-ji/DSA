#include <bits/stdc++.h>
using namespace std;

class Solution {
    bool bfs(int node,vector<int> &vis,vector<int> adj[],int n){
        vector<int> parent(n,-1);
        queue<int> q;
        q.push(node);
        vis[node] = 1;

        while(!q.empty()){
            int nn = q.front();
            q.pop();

            for(auto i : adj[nn]){
                if(!vis[i]){
                    q.push(i);
                    vis[i] = 1;
                    parent[i] = nn;
                }
                else if(parent[nn]!=i){
                    return 1;
                }
            }
        }
        return 0;
    }
  public:
    bool isCycle(int V, vector<vector<int>>& edges) {
        vector<int> adj[V];
        vector<int> vis(V,0);

        for(auto i : edges){
            int u = i[0];
            int v = i[1];

            adj[u].push_back(v);
            adj[v].push_back(u);
        }

        for(int i=0;i<V;i++){
            if(!vis[i]){
                bool res = bfs(i,vis,adj,V);
                if(res) return 1;
            }
        }
        return 0;
    }
};

int main() {
    return 0;
}