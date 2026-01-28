#include <bits/stdc++.h>
using namespace std;

class Solution {
    void solve(vector<vector<int>> &maze,vector<vector<int>> &vis,int r,int c,string s,vector<string> &ans){
        if(r<0 || c<0 || r>=maze.size() || c>=maze[0].size() || maze[r][c]==0 || vis[r][c]){
            return;
        }
        if(r==maze.size()-1 && c==maze[0].size()-1){
            ans.push_back(s);
            return;
        }
        vis[r][c] = 1;

        int dr[] = {1,0,-1,0};
        int dc[] = {0,1,0,-1};
        char ch[] = {'D','R','U','L'};

        for(int i=0;i<4;i++){
            int nr = r + dr[i];
            int nc = c + dc[i];
            char cc = ch[i];

            solve(maze,vis,nr,nc,s+cc,ans);
        }
        vis[r][c] = 0;
    }
  public:
    vector<string> ratInMaze(vector<vector<int>>& maze) {
        vector<string> ans;
        int n = maze.size();
        int m = maze[0].size();

        if(maze[0][0]==0 || maze[n-1][m-1]==0){
            return ans;
        }

        vector<vector<int>> vis(n,vector<int> (m,0));
        solve(maze,vis,0,0,"",ans);
        sort(ans.begin(),ans.end());
        return ans;
    }
};

int main() {
    return 0;
}