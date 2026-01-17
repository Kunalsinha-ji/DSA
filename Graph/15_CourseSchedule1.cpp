#include <bits/stdc++.h>
using namespace std;

class Solution {
    bool dfs(int node,vector<int> adj[],vector<int> &vis,vector<int> &dfsVis){
        vis[node] = 1;
        dfsVis[node] = 1;

        for(auto it: adj[node]){
            if(!vis[it]){
                bool res = dfs(it,adj,vis,dfsVis);
                if(res) return 1;
            }
            else if(dfsVis[it]){
                return 1;
            }
        }
        dfsVis[node] = 0;
        return 0;
    }
public:
    bool canFinish(int numCourses, vector<vector<int>>& prerequisites) {
        vector<int> adj[numCourses];
        vector<int> vis(numCourses,0), dfsVis(numCourses,0);

        for(auto it: prerequisites){
            int v = it[0];
            int u = it[1];

            adj[u].push_back(v);
        }

        for(int i=0;i<numCourses;i++){
            if(!vis[i]){
                bool res = dfs(i,adj,vis,dfsVis);
                if(res) return 0;
            }
        }
        return 1;
    }
};

int main() {
    return 0;
}