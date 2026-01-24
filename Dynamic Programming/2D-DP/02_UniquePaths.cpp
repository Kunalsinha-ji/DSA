#include <bits/stdc++.h>
using namespace std;

class Solution {
    int solve(int m,int n){
        if(m==1 && n==1){
            return 1;
        }
        if(m==0 || n==0){
            return 0;
        }

        int left = solve(m,n-1);
        int top = solve(m-1,n);

        return left + top;
    }

    int solve(int m,int n, vector<vector<int>> &dp){
        if(m==1 && n==1){
            return 1;
        }
        if(m==0 || n==0){
            return 0;
        }
        if(dp[m][n]!=-1)    return dp[m][n];

        int left = solve(m,n-1,dp);
        int top = solve(m-1,n,dp);

        return dp[m][n] = left + top;
    }
public:
    int uniquePaths(int m, int n) {
        // // Recursive
        // return solve(m,n);

        // // Memoization
        // vector<vector<int>> dp(m+1,vector<int> (n+1,-1));
        // return solve(m,n,dp);

        // // Tabulation
        // vector<vector<int>> dp(m+1,vector<int> (n+1,0));
        // dp[1][1] = 1;
        // for(int i=1;i<=m;i++){
        //     for(int j=1;j<=n;j++){
        //         if(i==1 && j==1)    continue;
        //         int left = dp[i][j-1];
        //         int top = dp[i-1][j];

        //         dp[i][j] = left + top;
        //     }
        // }
        // return dp[m][n];

        // Space optimization
        vector<int> prev(n+1,0), curr(n+1,0);
        prev[1] = curr[1] = 1;
        for(int i=1;i<=m;i++){
            for(int j=1;j<=n;j++){
                if(i==1 && j==1)    continue;
                int left = curr[j-1];
                int top = prev[j];

                curr[j] = left + top;
            }
            prev = curr;
        }
        return prev[n];
    }
};

int main() {
    return 0;
}