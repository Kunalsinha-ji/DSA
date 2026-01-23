#include <bits/stdc++.h>
using namespace std;

class Solution {
    int solve(vector<int> &heights, int i,int k){
        if(i==0){
            return 0;
        }

        int res = 1e9;
        for(int j=1;j<=k;j++){
            if(i-j>=0){
                int curr_res = solve(heights,i-j,k) + abs(heights[i] - heights[i-j]);
                res = min(curr_res,res);
            }
        }
        return res;
    }

    int solve(vector<int> &heights, int i,int k, vector<int> &dp){
        if(i==0){
            return 0;
        }
        if(dp[i]!=-1)   return dp[i];

        int res = 1e9;
        for(int j=1;j<=k;j++){
            if(i-j>=0){
                int curr_res = solve(heights,i-j,k,dp) + abs(heights[i] - heights[i-j]);
                res = min(curr_res,res);
            }
        }
        return dp[i] = res;
    }

public:
    int frogJump(vector<int>& heights, int k) {
        int n = heights.size();

        // // Recursive
        // return solve(heights,n-1,k);

        // // Memoization
        // vector<int> dp(n,-1);
        // return solve(heights,n-1,k,dp);

        // Tabulation
        vector<int> dp(n,1e9);
        dp[0] = 0;

        for(int i=1;i<n;i++){
            int res = 1e9;
            for(int j=1;j<=k;j++){
                if(i-j>=0){
                    int curr_res = dp[i-j] + abs(heights[i] - heights[i-j]);
                    res = min(curr_res,res);
                }
            }
            dp[i] = res;
        }
        return dp[n-1];
    }
};


int main() {
    return 0;
}