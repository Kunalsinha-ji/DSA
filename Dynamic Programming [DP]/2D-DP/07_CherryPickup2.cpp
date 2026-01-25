#include <bits/stdc++.h>
using namespace std;

class Solution {
    int solve(int j1,int j2,int i,int n,vector<vector<int>> &grid){
        if(j1<0 || j2<0 || j1>=grid[i].size() || j2>=grid[i].size()){
            return 0;
        }
        if(i==n-1){
            if(j1==j2){
                return grid[i][j1];
            }
            else{
                return grid[i][j1] + grid[i][j2];
            }
        }

        int res = 0;
        for(int k1=-1;k1<=1;k1++){
            for(int k2=-1;k2<=1;k2++){
                int nj1 = j1 + k1;
                int nj2 = j2 + k2;

                res = max(res,solve(nj1,nj2,i+1,n,grid));
            }
        }
        if(j1==j2){
            return res + grid[i][j1];
        }
        else{
            return res + grid[i][j1] + grid[i][j2];
        }
    }

    int solve(int j1,int j2,int i,int n,vector<vector<int>> &grid, vector<vector<vector<int>>> &dp){
        if(j1<0 || j2<0 || j1>=grid[i].size() || j2>=grid[i].size()){
            return 0;
        }
        if(i==n-1){
            if(j1==j2){
                return grid[i][j1];
            }
            else{
                return grid[i][j1] + grid[i][j2];
            }
        }
        if(dp[i][j1][j2]!=-1)   return dp[i][j1][j2];

        int res = 0;
        for(int k1=-1;k1<=1;k1++){
            for(int k2=-1;k2<=1;k2++){
                int nj1 = j1 + k1;
                int nj2 = j2 + k2;

                res = max(res,solve(nj1,nj2,i+1,n,grid,dp));
            }
        }
        if(j1==j2){
            return dp[i][j1][j2] = res + grid[i][j1];
        }
        else{
            return dp[i][j1][j2] = res + grid[i][j1] + grid[i][j2];
        }
    }
public:
    int cherryPickup(vector<vector<int>>& grid) {
        int n = grid.size(),m = grid[0].size();

        // // Recursive
        // return solve(0,m-1,0,n,grid);

        // // Memoization
        // vector<vector<vector<int>>> dp(n,vector<vector<int>> (m,vector<int> (m,-1)));
        // return solve(0,m-1,0,n,grid,dp);

        // Tabulation
        vector<vector<vector<int>>> dp(n,vector<vector<int>> (m,vector<int> (m,0)));
        for(int j1=0;j1<m;j1++){
            for(int j2=0;j2<m;j2++){
                if(j1==j2){
                    dp[n-1][j1][j2] = grid[n-1][j1];
                }
                else{
                    dp[n-1][j1][j2] = grid[n-1][j1] + grid[n-1][j2];
                }
            }
        }

        for(int i=n-2;i>=0;i--){
            for(int j1=0;j1<m;j1++){
                for(int j2=0;j2<m;j2++){
                    int res = 0;
                    for(int k1=-1;k1<=1;k1++){
                        for(int k2=-1;k2<=1;k2++){
                            int nj1 = j1 + k1;
                            int nj2 = j2 + k2;

                            if(nj1<0 || nj2<0 || nj1>=m || nj2>=m)  continue;
                            res = max(res,dp[i+1][nj1][nj2]);
                        }
                    }
                    if(j1==j2){
                        dp[i][j1][j2] = res + grid[i][j1];
                    }
                    else{
                        dp[i][j1][j2] = res + grid[i][j1] + grid[i][j2];
                    }
                }
            }
        }
        return dp[0][0][m-1];
    }
};

int main() {
    return 0;
}