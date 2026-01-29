#include <bits/stdc++.h>
using namespace std;

class Solution {
    bool isSafe(int node,vector<int> adj[],int clr,vector<int> &color){
        for(auto it: adj[node]){
            if(color[it]==clr){
                return 0;
            }
        }
        return 1;
    }
    bool solve(int node,int n,vector<int> adj[],vector<int> &color,int clr){
        if(node==n){
            return 1;
        }

        for(int c=0;c<clr;c++){
            if(isSafe(node,adj,c,color)){
                color[node] = c;
                bool res = solve(node+1,n,adj,color,clr);
                if(res){
                    return 1;
                }
                color[node] = -1;
            }
        }
        return 0;
    }
  public:
    bool graphColoring(int v, vector<vector<int>> &edges, int m) {
        vector<int> adj[v];
        vector<int> color(v,-1);

        for(auto e: edges){
            int u = e[0];
            int v = e[1];

            adj[u].push_back(v);
            adj[v].push_back(u);
        }

        return solve(0,v,adj,color,m);
    }
};

int main() {
    return 0;
}