#include <bits/stdc++.h>
using namespace std;

// Using Kahn's Algorithm for Topological Sorting
class Solution {
  public:
    vector<int> topoSort(int V, vector<vector<int>>& edges) {
        // code here
        vector<int> adj[V];
        vector<int> inDegree(V,0);
        for(auto it: edges){
            int u = it[0];
            int v = it[1];

            adj[u].push_back(v);
            inDegree[v]++;
        }

        vector<int> ans;
        queue<int> q;

        for(int i=0;i<V;i++){
            if(inDegree[i]==0){
                q.push(i);
            }
        }

        while(!q.empty()){
            int node = q.front();
            q.pop();

            ans.push_back(node);

            for(auto it: adj[node]){
                inDegree[it]--;
                if(inDegree[it]==0){
                    q.push(it);
                }
            }

        }

        return ans;
    }
};
// Using DFS
class Solution {
    void dfs(int node, vector<int> &vis, vector<int> adj[], stack<int> &st){
        vis[node] = 1;

        for(auto i: adj[node]){
            if(!vis[i]){
                dfs(i,vis,adj, st);
            }
        }

        st.push(node);
    }
  public:
    vector<int> topoSort(int V, vector<vector<int>>& edges) {
        // code here
        vector<int> adj[V];
        for(auto it: edges){
            int u = it[0];
            int v = it[1];

            adj[u].push_back(v);
        }

        vector<int> vis(V,0), ans;
        stack<int> st;

        for(int i=0;i<V;i++){
            if(!vis[i]){
                dfs(i,vis,adj,st);
            }
        }

        while(!st.empty()){
            ans.push_back(st.top());
            st.pop();
        }

        return ans;
    }
};

int main() {
    return 0;
}