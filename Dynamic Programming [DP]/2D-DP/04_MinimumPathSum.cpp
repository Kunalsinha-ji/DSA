#include <bits/stdc++.h>
using namespace std;

class Solution {
    int solve(int i,int j, vector<vector<int>> &grid){
        if(i==0 || j==0){
            return 1e9;
        }
        if(i==1 && j==1){
            return grid[i-1][j-1];
        }

        int left = solve(i,j-1,grid);
        int top = solve(i-1,j,grid);

        int res = min(left,top);
        if(res!=1e9){
            return res + grid[i-1][j-1];
        }
        return 1e9;
    }

    int solve(int i,int j, vector<vector<int>> &grid,vector<vector<int>> &dp){
        if(i==0 || j==0){
            return 1e9;
        }
        if(i==1 && j==1){
            return grid[i-1][j-1];
        }
        if(dp[i][j]!=-1)    return dp[i][j];

        int left = solve(i,j-1,grid,dp);
        int top = solve(i-1,j,grid,dp);

        int res = min(left,top);
        if(res!=1e9){
            return dp[i][j] = res + grid[i-1][j-1];
        }
        return dp[i][j] = 1e9;
    }
public:
    int minPathSum(vector<vector<int>>& grid) {
        int n = grid.size(), m = grid[0].size();

        // // Recursive
        // return solve(n,m,grid);

        // // Memoization
        // vector<vector<int>> dp(n+1,vector<int> (m+1,-1));
        // return solve(n,m,grid,dp);

        // // Tabulation
        // vector<vector<int>> dp(n+1,vector<int> (m+1,1e9));
        // dp[1][1] = grid[0][0];

        // for(int i=1;i<=n;i++){
        //     for(int j=1;j<=m;j++){
        //         if(i==1 && j==1)    continue;
        //         int left = dp[i][j-1];
        //         int top = dp[i-1][j];

        //         int res = min(left,top);
        //         if(res!=1e9){
        //             dp[i][j] = res + grid[i-1][j-1];
        //         }
        //         else{
        //             dp[i][j] = 1e9;
        //         }
        //     }
        // }
        // return dp[n][m];

        // Space optimization
        vector<int> prev(m+1,1e9), curr(m+1,1e9);
        prev[1] = grid[0][0];

        for(int i=1;i<=n;i++){
            for(int j=1;j<=m;j++){
                if(i == 1 && j == 1){
                    curr[j] = grid[0][0];
                    continue;
                }
                int left = curr[j-1];
                int top = prev[j];

                int res = min(left,top);
                if(res!=1e9){
                    curr[j] = res + grid[i-1][j-1];
                }
                else{
                    curr[j] = 1e9;
                }
            }
            prev = curr;
        }
        return prev[m];
    }
};

int main() {
    return 0;
}