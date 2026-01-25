#include <bits/stdc++.h>
using namespace std;

class Solution {
    int solve(string &s1,string &s2,int i,int j){
        if(j==0){
            return 1;
        }
        if(i==0){
            return 0;
        }

        if(s1[i-1]==s2[j-1]){
            return solve(s1,s2,i-1,j-1) + solve(s1,s2,i-1,j);
        }
        else{
            return solve(s1,s2,i-1,j);
        }
    }
    int solve(string &s1,string &s2,int i,int j, vector<vector<int>> &dp){
        if(j==0){
            return 1;
        }
        if(i==0){
            return 0;
        }
        if(dp[i][j]!=-1)    return dp[i][j];

        if(s1[i-1]==s2[j-1]){
            return dp[i][j] = solve(s1,s2,i-1,j-1,dp) + solve(s1,s2,i-1,j,dp);
        }
        else{
            return dp[i][j] = solve(s1,s2,i-1,j,dp);
        }
    }
public:
    int numDistinct(string s, string t) {
        int n = s.size(), m = t.size();

        // // Recursive
        // return solve(s,t,n,m);

        // // Memoization
        // vector<vector<int>> dp(n+1,vector<int> (m+1,-1));
        // return solve(s,t,n,m,dp);

        // // Tabulation
        // vector<vector<int>> dp(n+1,vector<int> (m+1,0));
        // for(int i=0;i<=n;i++){
        //     dp[i][0] = 1;
        // }

        // for(int i=1;i<=n;i++){
        //     for(int j=1;j<=m;j++){
        //         if(s[i-1]==t[j-1]){
        //             dp[i][j] = dp[i-1][j-1] + dp[i-1][j];
        //         }
        //         else{
        //             dp[i][j] = dp[i-1][j];
        //         }
        //     }
        // }
        // return dp[n][m];

        // Space optimization
        vector<int> prev(m+1,0) ,curr(m+1,0);
        prev[0] = 1;

        for(int i=1;i<=n;i++){
            for(int j=0;j<=m;j++){
                if(j==0){
                    curr[j] = 1;
                    continue;
                }
                if(s[i-1]==t[j-1]){
                    curr[j] = prev[j-1] + prev[j];
                }
                else{
                    curr[j] = prev[j];
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