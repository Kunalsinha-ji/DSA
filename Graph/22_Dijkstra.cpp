#include <bits/stdc++.h>
using namespace std;

class Solution {
  public:
    vector<int> dijkstra(int V, vector<vector<int>> &edges, int src) {
        // Code here
        vector<int> dist(V,1e9);
        vector<pair<int,int>> adj[V];

        for(auto it: edges){
            adj[it[0]].push_back({it[1],it[2]});
            adj[it[1]].push_back({it[0],it[2]});
        }

        dist[src] = 0;

        priority_queue<pair<int,int>, vector<pair<int,int>>, greater<pair<int,int>>> q;

        q.push({0,src});

        while(!q.empty()){
            int dis = q.top().first;
            int node = q.top().second;
            q.pop();

            for(auto it: adj[node]){
                if(dist[it.first]>dis+it.second){
                    dist[it.first] = dis+it.second;
                    q.push({dis+it.second,it.first});
                }
            }
        }

        for(int i=0;i<V;i++){
            if(dist[i]==1e9){
                dist[i] = -1;
            }
        }
        return dist;
    }
};


int main() {
    return 0;
}