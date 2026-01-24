#include <bits/stdc++.h>
using namespace std;

class Solution {
    int solve(int i,int j,vector<vector<int>> &matrix){
        if(j<0 || j>=matrix[i].size()){
            return 1e9;
        }
        if(i==0){
            return matrix[i][j];
        }

        int up = solve(i-1,j,matrix);
        int left_up = solve(i-1,j-1,matrix);
        int right_up = solve(i-1,j+1,matrix);

        return min({up,right_up,left_up}) + matrix[i][j];
    }

    int solve(int i,int j,vector<vector<int>> &matrix,vector<vector<int>> &dp){
        if(j<0 || j>=matrix[i].size()){
            return 1e9;
        }
        if(i==0){
            return matrix[i][j];
        }
        if(dp[i][j]!=-1)    return dp[i][j];

        int up = solve(i-1,j,matrix,dp);
        int left_up = solve(i-1,j-1,matrix,dp);
        int right_up = solve(i-1,j+1,matrix,dp);

        return dp[i][j] = min({up,right_up,left_up}) + matrix[i][j];
    }
public:
    int minFallingPathSum(vector<vector<int>>& matrix) {
        int n = matrix.size();
        int m = matrix[0].size();
        int ans = 1e9;

        // // Recursive
        // for(int j=0;j<m;j++){
        //     int res = solve(n-1,j,matrix);
        //     ans = min(ans,res);
        // }
        // return ans;

        // // Memoization
        // vector<vector<int>> dp(n,vector<int> (m,-1));
        // for(int j=0;j<m;j++){
        //     int res = solve(n-1,j,matrix,dp);
        //     ans = min(ans,res);
        // }
        // return ans;

        // Tabulation
        vector<vector<int>> dp(n,vector<int> (m,1e9));
        for(int j=0;j<m;j++){
            dp[0][j] = matrix[0][j];
        }

        for(int i=1;i<n;i++){
            for(int j=0;j<m;j++){
                int res = 1e9;
                int up = dp[i-1][j];
                if(j>0){
                    int left_up = dp[i-1][j-1];
                    res = min(res,left_up);
                }
                if(j<m-1){
                    int right_up = dp[i-1][j+1];
                    res = min(res,right_up);
                }
                dp[i][j] = min(up,res) + matrix[i][j];
            }
        }

        for(int j=0;j<m;j++){
            ans = min(ans,dp[n-1][j]);
        }
        return ans;
    }
};

int main() {
    return 0;
}