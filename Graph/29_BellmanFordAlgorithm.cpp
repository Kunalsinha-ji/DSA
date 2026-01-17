#include <bits/stdc++.h>
using namespace std;

// User function Template for C++

class Solution {
  public:
    vector<int> bellmanFord(int V, vector<vector<int>>& edges, int src) {
        vector<int> dist(V,1e8);
        dist[src] = 0;

        for(int i=0;i<V-1;i++){
            for(auto it: edges){
                int n1 = it[0];
                int n2 = it[1];
                int dis = it[2];

                if(dist[n1]!=1e8 && dist[n2]>dist[n1]+dis){
                    dist[n2] = dist[n1]+dis;
                }
            }
        }

        for(auto it: edges){
            int n1 = it[0];
            int n2 = it[1];
            int dis = it[2];

            if(dist[n1]!=1e8 && dist[n2]>dist[n1]+dis){
                return {-1};
            }
        }
        return dist;
    }
};


int main() {
    return 0;
}