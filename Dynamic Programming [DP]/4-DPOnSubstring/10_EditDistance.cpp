#include <bits/stdc++.h>
using namespace std;

class Solution {
    int solve(string &s1,string &s2,int i,int j){
        if(j==0){
            return i;
        }
        if(i==0){
            return j;
        }

        if(s1[i-1]==s2[j-1]){
            return solve(s1,s2,i-1,j-1);
        }
        else{
            int remove = solve(s1,s2,i-1,j);
            int replace = solve(s1,s2,i-1,j-1);
            int insert = solve(s1,s2,i,j-1);

            return min({remove,replace,insert}) + 1;
        }
    }
    int solve(string &s1,string &s2,int i,int j, vector<vector<int>> &dp){
        if(j==0){
            return i;
        }
        if(i==0){
            return j;
        }
        if(dp[i][j]!=-1)    return dp[i][j];

        if(s1[i-1]==s2[j-1]){
            return dp[i][j] = solve(s1,s2,i-1,j-1,dp);
        }
        else{
            int remove = solve(s1,s2,i-1,j,dp);
            int replace = solve(s1,s2,i-1,j-1,dp);
            int insert = solve(s1,s2,i,j-1,dp);

            return dp[i][j] = min({remove,replace,insert}) + 1;
        }
    }
public:
    int minDistance(string word1, string word2) {
        int n = word1.size();
        int m = word2.size();

        // // Recursive
        // return solve(word1,word2,n,m);

        // // Memoization
        // vector<vector<int>> dp(n+1,vector<int> (m+1,-1));
        // return solve(word1,word2,n,m,dp);

        // // Tabulation
        // vector<vector<int>> dp(n+1,vector<int> (m+1,1e9));
        // for(int i=0;i<=n;i++){
        //     dp[i][0] = i;
        // }
        // for(int j=0;j<=m;j++){
        //     dp[0][j] = j;
        // }

        // for(int i=1;i<=n;i++){
        //     for(int j=1;j<=m;j++){
        //         if(word1[i-1]==word2[j-1]){
        //             dp[i][j] = dp[i-1][j-1];
        //         }
        //         else{
        //             int remove = dp[i-1][j];
        //             int replace = dp[i-1][j-1];
        //             int insert = dp[i][j-1];

        //             dp[i][j] = min({remove,replace,insert}) + 1;
        //         }
        //     }
        // }
        // return dp[n][m];

        // Space optimization
        vector<int> prev(m+1,1e9), curr(m+1,1e9);
        for(int j=0;j<=m;j++){
            prev[j] = j;
        }

        for(int i=1;i<=n;i++){
            for(int j=0;j<=m;j++){
                if(j==0){
                    curr[0] = i;
                    continue;
                }
                if(word1[i-1]==word2[j-1]){
                    curr[j] = prev[j-1];
                }
                else{
                    int remove = prev[j];
                    int replace = prev[j-1];
                    int insert = curr[j-1];

                    curr[j] = min({remove,replace,insert}) + 1;
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