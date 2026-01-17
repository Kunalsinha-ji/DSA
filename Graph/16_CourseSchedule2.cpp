#include <bits/stdc++.h>
using namespace std;

// Function to find order of courses. Using BFS (Kahn's Algorithm)
class Solution {
public:
    vector<int> findOrder(int n, vector<vector<int>>& prerequisites) {
        vector<int> ans = {};

        vector<int> adj[n];
        vector<int> inDegree(n,0);
        queue<int> q;

        for(auto it: prerequisites){
            int v = it[0];
            int u = it[1];

            adj[u].push_back(v);
            inDegree[v]++;
        }

        for(int i=0;i<n;i++){
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

        if(ans.size()==n)   return ans;
        return {};
    }
};

// Function to find order of courses. Using DFS
class Solution {
    bool dfs(int node,vector<int> adj[],vector<int> &vis,vector<int> &dfsVis,stack<int> &st){
        vis[node] = dfsVis[node] = 1;

        for(auto it : adj[node]){
            if(!vis[it]){
                bool res = dfs(it,adj,vis,dfsVis,st);
                if(res==1)  return 1;
            }
            else if(dfsVis[it]) return 1;
        }
        dfsVis[node] = 0;
        st.push(node);
        return 0;
    }
public:
    vector<int> findOrder(int n, vector<vector<int>>& prerequisites) {
        vector<int> adj[n];
        stack<int> st;
        vector<int> vis(n,0),dfsVis(n,0);

        for(auto it: prerequisites){
            int v = it[0];
            int u = it[1];

            adj[u].push_back(v);
        }

        for(int i=0;i<n;i++){
            if(!vis[i]){
                if(dfs(i,adj,vis,dfsVis,st)){
                    return {};
                }
            }
        }

        vector<int> ans;
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