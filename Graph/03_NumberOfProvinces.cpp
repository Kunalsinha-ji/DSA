#include <bits/stdc++.h>
using namespace std;

class Solution {
    void dfs(int node,vector<int> &vis,vector<int> adj[]){
        vis[node] = 1;

        for(auto it: adj[node]){
            if(!vis[it]){
                dfs(it,vis,adj);
            }
        }
    }
public:
    int findCircleNum(vector<vector<int>>& isConnected) {
        int n = isConnected.size();

        vector<int> adj[n];
        vector<int> vis(n,0);
        for(int i=0;i<n;i++){
            for(int j=0;j<n;j++){
                if(isConnected[i][j]){
                    adj[i].push_back(j);
                    adj[j].push_back(i);
                }
            }
        }

        int ans = 0;

        for(int i=0;i<n;i++){
            if(!vis[i]){
                dfs(i,vis,adj);
                ans++;
            }
        }
        return ans;
    }
};

int main() {
    return 0;
}