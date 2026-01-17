#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    void solve(vector<vector<char>>& grid) {
        // Code here
        int n = grid.size(),m = grid[0].size();

        queue<pair<int,int>> q;
        vector<vector<int>> vis(n,vector<int> (m,0));

        for(int i=0;i<n;i++){
            if(grid[i][0]=='O'){
                q.push({i,0});
                vis[i][0] = 1;
            }
            if(grid[i][m-1]=='O'){
                q.push({i,m-1});
                vis[i][m-1] = 1;
            }
        }

        for(int i=0;i<m;i++){
            if(grid[0][i]=='O'){
                q.push({0,i});
                vis[0][i] = 1;
            }
            if(grid[n-1][i]=='O'){
                q.push({n-1,i});
                vis[n-1][i] = 1;
            }
        }

        int dr[] = {1,0,-1,0};
        int dc[] = {0,1,0,-1};

        while(!q.empty()){
            int r = q.front().first;
            int c = q.front().second;
            q.pop();

            for(int i=0;i<4;i++){
                int nr = r + dr[i];
                int nc = c + dc[i];

                if(nr>=0 && nc>=0 && nr<n && nc<m && vis[nr][nc]==0 && grid[nr][nc]=='O'){
                    vis[nr][nc] = 1;
                    q.push({nr,nc});
                }
            }
        }

        for(int i=0;i<n;i++){
            for(int j=0;j<m;j++){
                if(grid[i][j]=='O' && vis[i][j]==0){
                    grid[i][j] = 'X';
                }
            }
        }
    }
};

int main() {
    return 0;
}