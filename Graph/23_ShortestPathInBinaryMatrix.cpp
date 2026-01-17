#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int shortestPathBinaryMatrix(vector<vector<int>>& grid) {
        if(grid[0][0]){
            return -1;
        }
        int n = grid.size(), m= grid[0].size();

        vector<vector<int>> dist(n,vector<int> (m,1e9));

        dist[0][0] = 1;
        priority_queue<pair<int,pair<int,int>>, vector<pair<int,pair<int,int>>>, greater<pair<int,pair<int,int>>>> q;
        q.push({1,{0,0}});

        while(!q.empty()){
            int r = q.top().second.first;
            int c = q.top().second.second;
            int dis = q.top().first;
            q.pop();

            for(int i=-1;i<=1;i++){
                for(int j=-1;j<=1;j++){
                    int nr = r + i;
                    int nc = c + j;

                    if(nr>=0 && nc>=0 && nr<n && nc<m && grid[nr][nc]==0 && dist[nr][nc]>dis+1){
                        dist[nr][nc] = dis+1;
                        q.push({dis+1,{nr,nc}});
                    }
                }
            }
        }
        return dist[n-1][m-1]==1e9? -1: dist[n-1][m-1];
    }
};

int main() {
    return 0;
}