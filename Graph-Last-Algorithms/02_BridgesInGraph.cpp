#include <bits/stdc++.h>
using namespace std;

class Solution {
    void dfs(int node,int parent,vector<int> adj[],vector<int> &vis,int *tin, int *low,
                    vector<vector<int>> &ans, int &timer){

        vis[node] = 1;
        tin[node] = low[node] = timer++;

        for(auto it: adj[node]){
            if(!vis[it]){
                dfs(it,node,adj,vis,tin,low,ans,timer);
                low[node] = min(low[node],low[it]);

                if(low[it]>tin[node]){
                    ans.push_back({node,it});
                }
            }
            else if(it!=parent){
                low[node] = min(low[node],low[it]);
            }
        }
    }
public:
    vector<vector<int>> criticalConnections(int n, vector<vector<int>>& connections) {
        vector<vector<int>> bridges;
        int tin[n];
        int low[n];

        vector<int> vis(n,0);
        vector<int> adj[n];

        for(auto it: connections){
            adj[it[0]].push_back(it[1]);
            adj[it[1]].push_back(it[0]);
        }

        // Perform dfs
        int timer = 1;
        for(int i=0;i<n;i++){
            if(!vis[i]){
                dfs(i,-1,adj,vis,tin,low,bridges,timer);
            }
        }
        return bridges;
    }
};

int main() {
    return 0;
}