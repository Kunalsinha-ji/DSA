#include <bits/stdc++.h>
using namespace std;

class Solution {
    int solve(string &s1,string &s2,int i,int j){
        if(i==0 || j==0){
            return 0;
        }

        if(s1[i-1]==s2[j-1]){
            return 1 + solve(s1,s2,i-1,j-1);
        }
        else{
            int op1 = solve(s1,s2,i-1,j);
            int op2 = solve(s1,s2,i,j-1);
            return max(op1,op2);
        }
    }
    int solve(string &s1,string &s2,int i,int j, vector<vector<int>> &dp){
        if(i==0 || j==0){
            return 0;
        }
        if(dp[i][j]!=-1)    return dp[i][j];

        if(s1[i-1]==s2[j-1]){
            return dp[i][j] = 1 + solve(s1,s2,i-1,j-1,dp);
        }
        else{
            int op1 = solve(s1,s2,i-1,j,dp);
            int op2 = solve(s1,s2,i,j-1,dp);
            return dp[i][j] = max(op1,op2);
        }
    }
public:
    int longestCommonSubsequence(string text1, string text2) {
        int n = text1.size();
        int m = text2.size();

        // // Recursive
        // return solve(text1,text2,n,m);

        // // Memoization
        // vector<vector<int>> dp(n+1,vector<int> (m+1,-1));
        // return solve(text1,text2,n,m,dp);

        // // Tabulation
        // vector<vector<int>> dp(n+1,vector<int> (m+1,0));

        // for(int i=1;i<=n;i++){
        //     for(int j=1;j<=m;j++){
        //         if(text1[i-1]==text2[j-1]){
        //             dp[i][j] = 1 + dp[i-1][j-1];
        //         }
        //         else{
        //             int op1 = dp[i-1][j];
        //             int op2 = dp[i][j-1];
        //             dp[i][j] = max(op1,op2);
        //         }
        //     }
        // }
        // return dp[n][m];

        // Space optimization
        vector<int> prev(m+1,0), curr (m+1,0);

        for(int i=1;i<=n;i++){
            for(int j=1;j<=m;j++){
                if(text1[i-1]==text2[j-1]){
                    curr[j] = 1 + prev[j-1];
                }
                else{
                    int op1 = prev[j];
                    int op2 = curr[j-1];
                    curr[j] = max(op1,op2);
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