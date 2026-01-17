#include <bits/stdc++.h>
using namespace std;

// Function to detect cycle in a directed graph. Using BFS (Kahn's Algorithm)
class Solution {
  public:
    bool isCyclic(int V, vector<vector<int>> &edges) {
        // code here
        vector<int> inDegree(V,0);
        vector<int> adj[V];

        for(auto i : edges){
            int u = i[0];
            int v = i[1];

            adj[u].push_back(v);
            inDegree[v]++;
        }

        queue<int> q;
        for(int i=0;i<V;i++){
            if(inDegree[i]==0){
                q.push(i);
            }
        }

        int c = 0;
        while(!q.empty()){
            int node = q.front();
            c++;
            q.pop();

            for(auto it: adj[node]){
                inDegree[it]--;
                if(inDegree[it]==0){
                    q.push(it);
                }
            }
        }

        if(c==V) return 0;
        return 1;
    }
};

// Function to detect cycle in a directed graph. Using DFS
class Solution {
    bool dfs(int node,vector<int> &vis,vector<int> &dfsVis,vector<int> adj[]){
        vis[node] = 1;
        dfsVis[node] = 1;

        for(auto it: adj[node]){
            if(!vis[it]){
                bool res = dfs(it,vis,dfsVis,adj);
                if(res){
                    return 1;
                }
            }
            else if(dfsVis[it]){
                return 1;
            }
        }

        dfsVis[node] = 0;
        return 0;
    }
  public:
    bool isCyclic(int V, vector<vector<int>> &edges) {
        // code here
        vector<int> adj[V];

        for(auto i : edges){
            int u = i[0];
            int v = i[1];

            adj[u].push_back(v);
        }

        vector<int> vis(V,0), dfsVis(V,0);

        for(int i=0;i<V;i++){
            if(!vis[i]){
                bool res = dfs(i,vis,dfsVis,adj);
                if(res){
                    return 1;
                }
            }
        }
        return 0;
    }
};

int main() {
    return 0;
}