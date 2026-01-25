#include <bits/stdc++.h>
using namespace std;

class Solution {
    int solve(vector<vector<int>> &grid, int i,int j){
        if(i==0 || j==0 || grid[i-1][j-1]){
            return 0;
        }
        if(i==1 && j==1){
            return 1;
        }

        int left = solve(grid,i,j-1);
        int top = solve(grid,i-1,j);

        return left + top;
    }

    int solve(vector<vector<int>> &grid, int i,int j,vector<vector<int>> &dp){
        if(i==0 || j==0 || grid[i-1][j-1]){
            return 0;
        }
        if(i==1 && j==1){
            return 1;
        }
        if(dp[i][j]!=-1)    return dp[i][j];

        int left = solve(grid,i,j-1,dp);
        int top = solve(grid,i-1,j,dp);

        return dp[i][j] = left + top;
    }
public:
    int uniquePathsWithObstacles(vector<vector<int>>& grid) {
        int n = grid.size(), m = grid[0].size();

        if(grid[0][0] || grid[n-1][m-1]){
            return 0;
        }

        // // Recursive
        // return solve(grid,n,m);

        // // Memoization
        // vector<vector<int>> dp(n+1,vector<int> (m+1,-1));
        // return solve(grid,n,m,dp);

        // // Tabulation
        // vector<vector<int>> dp(n+1,vector<int> (m+1,0));
        // dp[1][1] = 1;
        // for(int i=1;i<=n;i++){
        //     for(int j=1;j<=m;j++){
        //         if(i==1 && j==1)    continue;
        //         if(grid[i-1][j-1])  continue;
        //         int left = dp[i][j-1];
        //         int top = dp[i-1][j];

        //         dp[i][j] = left + top;
        //     }
        // }
        // return dp[n][m];

        // Space optimization
        vector<int> prev(m+1,0),curr (m+1,0);
        prev[1] = curr[1] = 1;
        for(int i=1;i<=n;i++){
            for(int j=1;j<=m;j++){
                if(grid[i-1][j-1]){
                    curr[j] = 0;
                    continue;
                }
                int left = curr[j-1];
                int top = prev[j];

                curr[j] = left + top;
            }
            prev = curr;
        }
        return prev[m];
    }
};

int main() {
    return 0;
}