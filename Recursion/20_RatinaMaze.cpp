#include <bits/stdc++.h>
using namespace std;

class Solution {
    void solve(vector<string> &ans,string s,vector<vector<int>> &maze,int i,int j,vector<vector<int>> &vis){
        if(i==maze.size()-1 && j==maze[0].size()-1){
            ans.push_back(s);
            return;
        }
        if(i<0 || j<0 || i>=maze.size() || j>=maze[0].size() || maze[i][j]==0 || vis[i][j]){
            return;
        }
        vis[i][j] = 1;

        int dr[] = {1,0,-1,0};
        int dc[] = {0,1,0,-1};
        char chars[] = {'D','R','U','L'};

        for(int k=0;k<4;k++){
            int r = i + dr[k];
            int c = j + dc[k];
            char ch = chars[k];

            s += ch;
            solve(ans,s,maze,r,c,vis);
            s.pop_back();
        }
        vis[i][j] = 0;
    }
  public:
    vector<string> ratInMaze(vector<vector<int>>& maze) {
        int n = maze.size(), m = maze[0].size();

        if(maze[0][0]==0 || maze[n-1][m-1]==0){
            return {};
        }

        vector<vector<int>> vis(n,vector<int> (m,0));
        vector<string> ans;
        string st = "";
        solve(ans,st,maze,0,0,vis);
        sort(ans.begin(),ans.end());
        return ans;
    }
};

int main() {
    return 0;
}