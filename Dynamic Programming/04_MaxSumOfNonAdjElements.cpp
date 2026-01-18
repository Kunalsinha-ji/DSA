#include <bits/stdc++.h>
using namespace std;

class Solution {
    int solve(vector<int> &nums, int i){
        if(i==1){
            return nums[i-1];
        }
        if(i==0){
            return 0;
        }

        int take = solve(nums,i-2) + nums[i-1];
        int ntake = solve(nums,i-1) + 0;

        return max(take,ntake);
    }

    int solve(vector<int> &nums, int i, vector<int> &dp){
        if(i==1){
            return nums[i-1];
        }
        if(i==0){
            return 0;
        }
        if(dp[i]!=-1)   return dp[i];

        int take = solve(nums,i-2,dp) + nums[i-1];
        int ntake = solve(nums,i-1,dp) + 0;

        return dp[i] = max(take,ntake);
    }
public:
    int rob(vector<int>& nums) {
        int n = nums.size();

        // // Recursive
        // return solve(nums,n);

        // // Memoization
        // vector<int> dp(n+1,-1);
        // return solve(nums,n,dp);

        // // Tabulation
        // vector<int> dp(n+1,0);
        // dp[1] = nums[0];

        // for(int i=2;i<=n;i++){
        //     int take = dp[i-2] + nums[i-1];
        //     int ntake = dp[i-1] + 0;

        //     dp[i] = max(take,ntake);
        // }
        // return dp[n];

        // Space Optimization
        int last1 = 0;
        int last = nums[0];

        for(int i=2;i<=n;i++){
            int take = last1 + nums[i-1];
            int ntake = last + 0;

            int curr = max(take,ntake);
            last1 = last;
            last = curr;
        }
        return last;
    }
};

int main() {
    return 0;
}