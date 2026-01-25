#include <bits/stdc++.h>
using namespace std;

class Solution {
    int solve(int i,int j,vector<vector<int>> &mat){
        if(i==0){
            return mat[i][j];
        }

        int res = 0;
        for(int k=0;k<mat[0].size();k++){
            if(k==j)    continue;
            int jj = solve(i-1,k,mat) + mat[i][j];
            res = max(jj,res);
        }
        return res;
    }

    int solve(int i,int j,vector<vector<int>> &mat,vector<vector<int>> &dp){
        if(i==0){
            return mat[i][j];
        }
        if(dp[i][j]!=-1)    return dp[i][j];

        int res = 0;
        for(int k=0;k<mat[0].size();k++){
            if(k==j)    continue;
            int jj = solve(i-1,k,mat,dp) + mat[i][j];
            res = max(jj,res);
        }
        return dp[i][j] = res;
    }
  public:
    int maximumPoints(vector<vector<int>>& mat) {
        int n = mat.size();
        int m = mat[0].size();

        // // Recursive
        // int res = 0;
        // for(int i=0;i<m;i++){
        //     int k = solve(n-1,i,mat);
        //     res = max(res,k);
        // }
        // return res;

        // // Memoization
        // int res = 0;
        // vector<vector<int>> dp(n,vector<int> (m,-1));
        // for(int i=0;i<m;i++){
        //     int k = solve(n-1,i,mat,dp);
        //     res = max(res,k);
        // }
        // return res;

        // // Tabulation
        // vector<vector<int>> dp(n,vector<int> (m,0));
        // for(int i=0;i<m;i++){
        //     dp[0][i] = mat[0][i];
        // }

        // for(int i=1;i<n;i++){
        //     for(int j=0;j<m;j++){
        //         int res = 0;
        //         for(int k=0;k<mat[0].size();k++){
        //             if(k==j)    continue;
        //             int jj = dp[i-1][k] + mat[i][j];
        //             res = max(jj,res);
        //         }
        //         dp[i][j] = res;
        //     }
        // }
        // int res = 0;
        // for(int i=0;i<m;i++){
        //     res = max(res,dp[n-1][i]);
        // }
        // return res;

        // Space optimization
        vector<int> prev(m),curr(m);
        for(int i=0;i<m;i++){
            prev[i] = mat[0][i];
            curr[i] = mat[0][i];
        }

        for(int i=1;i<n;i++){
            for(int j=0;j<m;j++){
                int res = 0;
                for(int k=0;k<m;k++){
                    if(k==j)    continue;
                    int jj = prev[k] + mat[i][j];
                    res = max(jj,res);
                }
                curr[j] = res;
            }
            prev = curr;
        }
        int res = 0;
        for(int i=0;i<m;i++){
            res = max(res,prev[i]);
        }
        return res;
    }
};

int main() {
    return 0;
}