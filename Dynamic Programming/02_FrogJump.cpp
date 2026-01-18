#include <bits/stdc++.h>
using namespace std;

class Solution {
    // Recursive Solution
    int solve(vector<int> &heights,int i){
        if(i>=heights.size()-1){
            return 0;
        }

        int op1 = solve(heights,i+1) + abs(heights[i+1]-heights[i]);
        if(i<heights.size()-2){
            int op2 = solve(heights,i+2) + abs(heights[i+2]-heights[i]);
            op1 = min(op1,op2);
        }
        return op1;
    }

    // Memoization Solution
    int solve(vector<int> &heights,int i, vector<int> &dp){
        if(i>=heights.size()-1){
            return 0;
        }
        if(dp[i]!=-1)   return dp[i];

        int op1 = solve(heights,i+1,dp) + abs(heights[i+1]-heights[i]);
        if(i<heights.size()-2){
            int op2 = solve(heights,i+2,dp) + abs(heights[i+2]-heights[i]);
            op1 = min(op1,op2);
        }
        return dp[i] = op1;
    }
  public:
    int minCost(vector<int>& height) {
        int n = height.size();

        // // Recursive
        // return solve(height,0);

        // // Memoization
        // vector<int> dp(n,-1);
        // return solve(height,0,dp);

        // // Tabulation Solution
        // vector<int> dp(n,1e9);
        // dp[n-1] = 0;
        // for(int i=n-2;i>=0;i--){
        //     int op1 = dp[i+1] + abs(height[i+1]-height[i]);
        //     if(i<n-2){
        //         int op2 = dp[i+2] + abs(height[i+2]-height[i]);
        //         op1 = min(op1,op2);
        //     }
        //     dp[i] = op1;
        // }
        // return dp[0];

        // Space optimization solution
        int last1 = 0, last = 0;
        for(int i=n-2;i>=0;i--){
            int op1 = last + abs(height[i+1]-height[i]);
            if(i<n-2){
                int op2 = last1 + abs(height[i+2]-height[i]);
                op1 = min(op1,op2);
            }
            last1 = last;
            last = op1;
        }
        return last;
    }
};

int main() {
    return 0;
}