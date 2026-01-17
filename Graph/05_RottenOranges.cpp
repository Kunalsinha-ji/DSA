#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int orangesRotting(vector<vector<int>>& grid) {
        int n = grid.size();
        int m = grid[0].size();

        int dr[]= {1,0,-1,0};
        int dc[]= {0,1,0,-1};

        queue<pair<int,pair<int,int>>> q;
        vector<vector<int>> dist(n,vector<int> (m,1e9));

        for(int i=0;i<n;i++){
            for(int j=0;j<m;j++){
                if(grid[i][j]==2){
                    dist[i][j] = 0;
                    q.push({0,{i,j}});
                }
            }
        }

        while(!q.empty()){
            int time = q.front().first;
            int r = q.front().second.first;
            int c = q.front().second.second;
            q.pop();

            for(int i=0;i<4;i++){
                int nr = r + dr[i];
                int nc = c + dc[i];

                if(nr>=0 && nc>=0 && nr<n && nc<m && grid[nr][nc]==1 && dist[nr][nc]>time + 1){
                    dist[nr][nc] = time+1;
                    q.push({time+1,{nr,nc}});
                }
            }
        }

        int ans = 0;
        for(int i=0;i<n;i++){
            for(int j=0;j<m;j++){
                if(grid[i][j]==1){
                    if(dist[i][j]==1e9) return -1;
                    ans = max(ans,dist[i][j]);
                }
            }
        }
        return ans;
    }
};

int main() {
    return 0;
}