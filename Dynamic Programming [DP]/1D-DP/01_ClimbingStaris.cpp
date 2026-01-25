#include <bits/stdc++.h>
using namespace std;

class Solution {
    int solve(int n){
        if(n<=1){
            return 1;
        }

        return solve(n-1) + solve(n-2);
    }

    int solve(int n,vector<int> &dp){
        if(n<=1){
            return 1;
        }
        if(dp[n]!=-1)   return dp[n];

        return dp[n] = solve(n-1,dp) + solve(n-2,dp);
    }
public:
    int climbStairs(int n) {
        // // recursive
        // return solve(n);

        // // Memoization
        // vector<int> dp(n+1,-1);
        // return solve(n,dp);

        // // Tabulation
        // vector<int> dp(n+1);
        // dp[0] = dp[1] = 1;

        // for(int i=2;i<=n;i++){
        //     dp[i] = dp[i-1] + dp[i-2];
        // }
        // return dp[n];

        // Space optimization
        int last = 1,last1 = 1;

        for(int i=2;i<=n;i++){
            int curr = last + last1;
            last1 = last;
            last = curr;
        }
        return last;
    }
};

int main() {
    return 0;
}