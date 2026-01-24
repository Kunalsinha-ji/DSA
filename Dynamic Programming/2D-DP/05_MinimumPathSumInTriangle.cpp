#include <bits/stdc++.h>
using namespace std;

class Solution {
    int solve(int i,int j,vector<vector<int>> &triangle){
        if(j>=triangle[i].size()){
            return 1e9;
        }
        if(i==triangle.size()-1){
            return triangle[i][j];
        }

        int down = solve(i+1,j,triangle);
        int diag = solve(i+1,j+1,triangle);

        int res = min(down,diag);
        if(res==1e9){
            return 1e9;
        }
        else{
            return res + triangle[i][j];
        }
    }

    int solve(int i,int j,vector<vector<int>> &triangle, vector<vector<int>> &dp){
        if(j>=triangle[i].size()){
            return 1e9;
        }
        if(i==triangle.size()-1){
            return triangle[i][j];
        }
        if(dp[i][j]!=-1)    return dp[i][j];

        int down = solve(i+1,j,triangle,dp);
        int diag = solve(i+1,j+1,triangle,dp);

        int res = min(down,diag);
        if(res==1e9){
            return dp[i][j] = 1e9;
        }
        else{
            return dp[i][j] = res + triangle[i][j];
        }
    }
public:
    int minimumTotal(vector<vector<int>>& triangle) {
        int n = triangle.size();

        // // Recursive
        // return solve(0,0,triangle);

        // // Memoization
        // vector<vector<int>> dp(n,vector<int> (n,-1));
        // return solve(0,0,triangle,dp);

        // // Tabulation
        // vector<vector<int>> dp(n,vector<int> (n,1e9));
        // for(int i=0;i<n;i++){
        //     dp[n-1][i] = triangle[n-1][i];
        // }

        // for(int i=n-2;i>=0;i--){
        //     for(int j=0;j<triangle[i].size();j++){
        //         int down = dp[i+1][j];
        //         int diag = dp[i+1][j+1];

        //         int res = min(down,diag);
        //         if(res==1e9){
        //             dp[i][j] = 1e9;
        //         }
        //         else{
        //             dp[i][j] = res + triangle[i][j];
        //         }
        //     }
        // }
        // return dp[0][0];

        // Space optimization
        vector<int> prev(n,1e9), curr(n);
        for(int i=0;i<n;i++){
            prev[i] = triangle[n-1][i];
        }

        for(int i=n-2;i>=0;i--){
            for(int j=0;j<triangle[i].size();j++){
                int down = prev[j];
                int diag = prev[j+1];

                int res = min(down,diag);
                if(res==1e9){
                    curr[j] = 1e9;
                }
                else{
                    curr[j] = res + triangle[i][j];
                }
            }
            prev = curr;
        }
        return prev[0];
    }
};

int main() {
    return 0;
}