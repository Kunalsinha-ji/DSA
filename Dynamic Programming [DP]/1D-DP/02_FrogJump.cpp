#include <bits/stdc++.h>
using namespace std;

class Solution {
    int solve(vector<int> &height,int i){
        if(i==0){
            return 0;
        }

        int op1 = solve(height,i-1) + abs(height[i]-height[i-1]);
        if(i>=2){
            int op2 = solve(height,i-2) + abs(height[i]-height[i-2]);
            op1 = min(op1,op2);
        }
        return op1;
    }

    int solve(vector<int> &height,int i, vector<int> &dp){
        if(i==0){
            return 0;
        }
        if(dp[i]!=-1)   return dp[i];

        int op1 = solve(height,i-1,dp) + abs(height[i]-height[i-1]);
        if(i>=2){
            int op2 = solve(height,i-2,dp) + abs(height[i]-height[i-2]);
            op1 = min(op1,op2);
        }
        return dp[i] = op1;
    }
  public:
    int minCost(vector<int>& height) {
        int n = height.size();

        // // Recursive
        // return solve(height,n-1);

        // // Memoization
        // vector<int> dp(n,-1);
        // return solve(height,n-1,dp);

        // // Tabulation
        // vector<int> dp(n);
        // dp[0] = 0;
        // for(int i=1;i<n;i++){
        //     int op1 = dp[i-1] + abs(height[i]-height[i-1]);
        //     if(i>=2){
        //         int op2 = dp[i-2] + abs(height[i]-height[i-2]);
        //         op1 = min(op1,op2);
        //     }
        //     dp[i] = op1;
        // }
        // return dp[n-1];

        // Space optimization
        int last = 0,last1 = 0;

        for(int i=1;i<n;i++){
            int op1 = last + abs(height[i]-height[i-1]);
            if(i>=2){
                int op2 = last1 + abs(height[i]-height[i-2]);
                op1 = min(op1,op2);
            }
            int curr = op1;
            last1 = last;
            last = curr;
        }
        return last;
    }
};

int main() {
    return 0;
}