#include <bits/stdc++.h>
using namespace std;

// User function Template for C++
class Solution {
    void dfs(vector<vector<int>> &grid, vector<vector<int>> &vis,int r,int c,
             vector<pair<int,int>> &v,int sr,int sc){
        int n = grid.size(), m = grid[0].size();
        vis[r][c] = 1;
        v.push_back({r-sr,c-sc});

        int dr[] = {1,0,-1,0};
        int dc[] = {0,1,0,-1};

        for(int i=0;i<4;i++){
            int nr = r + dr[i];
            int nc = c + dc[i];

            if(nr>=0 && nc>=0 && nr<n && nc<m && grid[nr][nc] && vis[nr][nc]==0){
                dfs(grid,vis,nr,nc,v,sr,sc);
            }
        }
    }
  public:
    int countDistinctIslands(vector<vector<int>>& grid) {
        int n = grid.size(),m= grid[0].size();
        set<vector<pair<int,int>>> st;
        vector<vector<int>> vis(n,vector<int> (m,0));

        for(int i=0;i<n;i++){
            for(int j=0;j<m;j++){
                vector<pair<int,int>> v;
                if(grid[i][j] && vis[i][j]==0){
                    dfs(grid,vis,i,j,v,i,j);
                    st.insert(v);
                }
            }
        }
        return st.size();
    }
};


int main() {
    return 0;
}