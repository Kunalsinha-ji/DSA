#include <bits/stdc++.h>
using namespace std;

class Solution {
    bool solve(vector<vector<char>> &board,string &word,int i,int j,int ind,vector<vector<int>> &vis){
        if(ind==word.size()){
            return 1;
        }
        if(i<0 || j<0 || i>=board.size() || j>=board[0].size() || board[i][j]!=word[ind] || vis[i][j]){
            return 0;
        }

        vis[i][j] = 1;
        int dr[] = {1,0,-1,0};
        int dc[] = {0,1,0,-1};

        for(int k=0;k<4;k++){
            int r = i + dr[k];
            int c = j + dc[k];

            bool kk = solve(board,word,r,c,ind+1,vis);
            if(kk){
                return 1;
            }
        }
        vis[i][j] = 0;
        return 0;
    }
public:
    bool exist(vector<vector<char>>& board, string word) {
        int n = board.size();
        int m = board[0].size();

        vector<vector<int>> vis(n,vector<int> (m,0));
        for(int i=0;i<n;i++){
            for(int j=0;j<m;j++){
                if(board[i][j]==word[0]){
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