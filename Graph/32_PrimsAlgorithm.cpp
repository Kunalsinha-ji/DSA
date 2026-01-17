#include <bits/stdc++.h>
using namespace std;

// Prim's Algorithm to find the Minimum Spanning Tree (MST) of a graph
class Solution {
  public:
    int spanningTree(int V, vector<vector<int>>& edges) {
        // code here
        int sum = 0;
        priority_queue<pair<int,int>, vector<pair<int,int>>, greater<pair<int,int>>> pq;
        vector<pair<int,int>> adj[V];
        vector<int> vis(V,0);

        for(auto it: edges){
            int u = it[0];
            int v = it[1];
            int w = it[2];

            adj[u].push_back({v,w});
            adj[v].push_back({u,w});
        }

        pq.push({0,0});

        while(!pq.empty()){
            int node = pq.top().second;
            int wt = pq.top().first;
            pq.pop();

            if(vis[node]==1){
                continue;
            }
            vis[node] = 1;
            sum += wt;

            for(auto it : adj[node]){
                if(!vis[it.first]){
                    pq.push({it.second,it.first});
                }
            }
        }
        return sum;
    }
};

int main() {
    return 0;
}