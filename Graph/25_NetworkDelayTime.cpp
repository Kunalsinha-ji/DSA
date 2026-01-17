#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int networkDelayTime(vector<vector<int>>& times, int n, int k) {
        // Code here
        vector<int> dist(n+1,1e9);
        vector<pair<int,int>> adj[n+1];

        for(auto it: times){
            adj[it[0]].push_back({it[1],it[2]});
        }

        dist[k] = 0;

        priority_queue<pair<int,int>, vector<pair<int,int>>, greater<pair<int,int>>> q;

        q.push({0,k});

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
        int maxi = 0;
        for(int i=1;i<=n;i++){
            if(dist[i]==1e9){
                return -1;
            }
            maxi = max(maxi,dist[i]);
        }
        return maxi;
    }
};

int main() {
    return 0;
}