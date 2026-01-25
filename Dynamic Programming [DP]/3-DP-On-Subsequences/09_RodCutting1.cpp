#include <bits/stdc++.h>
using namespace std;

// User function Template for C++

class Solution {
    int solve(vector<int> &price,int i,int len){
        if(len==0){
            return 0;
        }
        if(i==0){
            return len * price[i];
        }

        int ntake = solve(price,i-1,len);
        if(len>=i+1){
            int take = solve(price,i,len-i-1) + price[i];
            ntake = max(ntake,take);
        }
        return ntake;
    }
    int solve(vector<int> &price,int i,int len, vector<vector<int>> &dp){
        if(len==0){
            return 0;
        }
        if(i==0){
            return len * price[i];
        }
        if(dp[i][len]!=-1)  return dp[i][len];

        int ntake = solve(price,i-1,len,dp);
        if(len>=i+1){
            int take = solve(price,i,len-i-1,dp) + price[i];
            ntake = max(ntake,take);
        }
        return dp[i][len] = ntake;
    }
  public:
    int cutRod(vector<int> &price) {
        int n = price.size();

        // // Recursive
        // return solve(price,n-1,n);

        // // Memoization
        // vector<vector<int>> dp(n,vector<int> (n+1,-1));
        // return solve(price,n-1,n,dp);

        // // Tabulation
        // vector<vector<int>> dp(n,vector<int> (n+1,0));
        // for(int len=0;len<=n;len++){
        //     dp[0][len] = len * price[0];
        // }

        // for(int i=1;i<n;i++){
        //     for(int len=0;len<=n;len++){
        //         int ntake = dp[i-1][len];
        //         if(len>=i+1){
        //             int take = dp[i][len-i-1] + price[i];
        //             ntake = max(ntake,take);
        //         }
        //         dp[i][len] = ntake;
        //     }
        // }
        // return dp[n-1][n];

        // Space optimization
        vector<int> prev(n+1,0), curr(n+1,0);
        for(int len=0;len<=n;len++){
            prev[len] = len * price[0];
        }

        for(int i=1;i<n;i++){
            for(int len=0;len<=n;len++){
                int ntake = prev[len];
                if(len>=i+1){
                    int take = curr[len-i-1] + price[i];
                    ntake = max(ntake,take);
                }
                curr[len] = ntake;
            }
            prev = curr;
        }
        return prev[n];
    }
};

int main() {
    return 0;
}