#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    vector<vector<int>> updateMatrix(vector<vector<int>>& mat) {
        int n = mat.size();
        int m = mat[0].size();

        vector<vector<int>> dist(n,vector<int> (m,1e9));
        queue<pair<int,pair<int,int>>> q;

        for(int i=0;i<n;i++){
            for(int j=0;j<m;j++){
                if(mat[i][j]==0){
                    q.push({0,{i,j}});
                    dist[i][j] = 0;
                }
            }
        }

        int dr[] = {1,0,-1,0};
        int dc[] = {0,1,0,-1};

        while(!q.empty()){
            int r = q.front().second.first;
            int c = q.front().second.second;
            int dis = q.front().first;
            q.pop();

            for(int i=0;i<4;i++){
                int nr = r + dr[i];
                int nc = c + dc[i];

                if(nr>=0 && nc>=0 && nr<n && nc<m && mat[nr][nc]==1 && dis+1<dist[nr][nc]){
                    dist[nr][nc] = dis+1;
                    q.push({dis+1,{nr,nc}});
                }
            }
        }
        return dist;
    }
};

int main() {
    return 0;
}