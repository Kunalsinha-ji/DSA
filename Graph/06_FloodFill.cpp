#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    vector<vector<int>> floodFill(vector<vector<int>>& image, int sr, int sc, int color) {
        int n = image.size();
        int m = image[0].size();

        int dr[] = {1,0,-1,0};
        int dc[] = {0,1,0,-1};

        vector<vector<int>> ans = image;
        vector<vector<int>> vis(n,vector<int> (m,0));

        int target = image[sr][sc];

        queue<pair<int,int>> q;
        q.push({sr,sc});

        while(!q.empty()){
            int r = q.front().first;
            int c = q.front().second;
            q.pop();

            ans[r][c] = color;

            for(int i=0;i<4;i++){
                int nr = r + dr[i];
                int nc = c + dc[i];

                if(nr>=0 && nc>=0 && nr<n && nc<m && image[nr][nc]==target && vis[nr][nc]==0){
                    vis[nr][nc] = 1;
                    q.push({nr,nc});
                }
            }
        }
        return ans;
    }
};

int main() {
    return 0;
}