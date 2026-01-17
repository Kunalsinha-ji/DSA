#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int findCheapestPrice(int n, vector<vector<int>>& flights, int src, int dst, int k) {
        vector<int> dist(n,1e9);
        vector<pair<int,int>> adj[n];

        for(auto it: flights){
            int u = it[0];
            int v = it[1];
            int d = it[2];

            adj[u].push_back({v,d});
        }

        priority_queue<pair<int,pair<int,int>>, vector<pair<int,pair<int,int>>>, greater<pair<int,pair<int,int>>>> q;
        q.push({0,{0,src}});

        while(!q.empty()){
            int stops = q.top().first;
            int dis = q.top().second.first;
            int node = q.top().second.second;
            q.pop();

            if(stops>k){
                continue;
            }

            for(auto it: adj[node]){
                int nn = it.first;
                int d = it.second;

                if(dist[nn]>d+dis){
                    dist[nn] = d+dis;
                    q.push({stops+1,{dist[nn],nn}});
                }
            }
        }

        return dist[dst] == 1e9? -1: dist[dst];
    }
};

int main() {
    return 0;
}