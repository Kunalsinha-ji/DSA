#include <bits/stdc++.h>
using namespace std;

class Solution {
  public:
    vector<int> shortestPath(int V, vector<vector<int>> &edges, int src) {
        // code here
        vector<int> dist(V,1e9);
        vector<int> adj[V];

        for(auto it: edges){
            adj[it[0]].push_back(it[1]);
            adj[it[1]].push_back(it[0]);
        }

        dist[src] = 0;

        queue<pair<int,int>> q;

        q.push({src,0});

        while(!q.empty()){
            int node = q.front().first;
            int dis = q.front().second;
            q.pop();

            for(auto it: adj[node]){
                if(dist[it]>dis+1){
                    dist[it] = dis+1;
                    q.push({it,dis+1});
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