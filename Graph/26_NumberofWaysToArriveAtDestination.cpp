#include <bits/stdc++.h>
using namespace std;

class Solution {
    int mod = 1e9+7;
public:
    int countPaths(int n, vector<vector<int>>& roads) {
        vector<pair<int,int>> adj[n];

        for(auto it: roads){
            int u = it[0];
            int v = it[1];
            int wt = it[2];

            adj[u].push_back({v,wt});
            adj[v].push_back({u,wt});
        }

        vector<int> dist(n,INT_MAX);
        vector<int> ways(n,0);

        dist[0] = 0;
        ways[0] = 1;

        priority_queue<pair<int,int>, vector<pair<int,int>>, greater<pair<int,int>>> pq;
        pq.push({0,0});

        while(!pq.empty()){
            int node = pq.top().second;
            int dis = pq.top().first;
            pq.pop();

            for(auto it: adj[node]){
                int nn = it.first;
                int wt = it.second;

                if(dist[nn]>wt+dis){
                    dist[nn] = (wt+dis)%mod;
                    ways[nn] = ways[node];
                    pq.push({dist[nn],nn});
                }
                else if(dist[nn]==dis+wt){
                    ways[nn] = (ways[nn] + ways[node])%mod;
                }
            }
        }
        return ways[n-1]%mod;
    }
};

int main() {
    return 0;
}