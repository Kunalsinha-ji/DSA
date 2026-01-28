#include <bits/stdc++.h>
using namespace std;

class Solution {
    bool solve(vector<vector<char>>& board, string &word,int r,int c,int i,vector<vector<int>> &vis){
        if(i==word.size()){
            return 1;
        }
        if(r<0 || c<0 || r>=board.size() || c>=board[0].size() || vis[r][c] || board[r][c]!=word[i]){
            return 0;
        }
        vis[r][c] = 1;

        int dr[] = {1,0,-1,0};
        int dc[] = {0,1,0,-1};

        for(int k=0;k<4;k++){
            int nr = r + dr[k];
            int nc = c + dc[k];

            bool res = solve(board,word,nr,nc,i+1,vis);
            if(res){
                return 1;
            }
        }
        vis[r][c] = 0;
        return 0;
    }
public:
    bool exist(vector<vector<char>>& board, string word) {
        int n = board.size();
        int m = board[0].size();

        vector<vector<int>> vis(n,vector<int> (m,0));

        for(int i=0;i<n;i++){
            for(int j=0;j<m;j++){
                if(word[0]==board[i][j]){
                    bool res = solve(board,word,i,j,0,vis);
                    if(res){
                        return 1;
                    }
                }
            }
        }
        return 0;
    }
};

int main() {
    return 0;
}