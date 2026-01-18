#include <bits/stdc++.h>
using namespace std;

class Solution {
    void dfs(int node,vector<vector<int>> &adj,vector<int> &vis,stack<int> &st){
        vis[node] = 1;

        for(auto it: adj[node]){
            if(!vis[it]){
                dfs(it,adj,vis,st);
            }
        }

        st.push(node);
    }

    void dfs(int node,vector<int> adj[],vector<int> &vis){
        vis[node] = 1;

        for(auto it: adj[node]){
            if(!vis[it]){
                dfs(it,adj,vis);
            }
        }
    }
  public:
    int kosaraju(vector<vector<int>> &adj) {
        int n = adj.size();

        stack<int> st;
        vector<int> vis(n,0);
        // Sort nodes on the basis on completion of DFS
        for(int i=0;i<n;i++){
            if(!vis[i]){
                dfs(i,adj,vis,st);
            }
        }

        // Reverse the edges: logic strongly connected componenets will be
        // reachable to each other even after reversing the edges
        vector<int> adjT[n];
        for(int i=0;i<n;i++){
            vis[i] = 0;
            for(auto it: adj[i]){
                adjT[it].push_back(i);
            }
        }

        // Perform dfs and count how many calls are made
        int scc = 0;

        while(!st.empty()){
            int node = st.top();
            st.pop();

            if(!vis[node]){
                dfs(node,adjT,vis);
                scc++;
            }
        }
        return scc;
    }
};

int main() {
    return 0;
}