#include <bits/stdc++.h>
using namespace std;

class Solution {
    bool solve(int node, vector<vector<int>> &adj, int col,vector<int> &color){
        color[node] = col;

        for(auto it: adj[node]){
            if(color[it]==-1){
                bool res = solve(it,adj,!col,color);
                if(res==0)    return 0;
            }
            else if(color[it]==col) return 0;
        }
        return 1;
    }
public:
    bool isBipartite(vector<vector<int>>& graph) {
        int n = graph.size();
        vector<int> color(n,-1);

        for(int i=0;i<n;i++){
            if(color[i]==-1){
                bool res = solve(i,graph,0,color);
                if(res==0)  return 0;
            }
        }
        return 1;
    }
};

int main() {
    return 0;
}