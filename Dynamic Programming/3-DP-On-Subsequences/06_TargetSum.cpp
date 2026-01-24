#include <bits/stdc++.h>
using namespace std;

class Solution {
    int solve(vector<int> &nums,int i,int sum){
        if(i==0){
            if((sum+nums[i]==0) & (sum-nums[i]==0)) {
                return 2;
            }
            return (sum+nums[i]==0) | (sum-nums[i]==0);
        }

        int add = solve(nums,i-1,sum+nums[i]);
        int sub = solve(nums,i-1,sum-nums[i]);

        return sub+add;
    }

    int solve(vector<int> &nums,int i,int sum, map<pair<int,int>,int> &dp){
        if(i==0){
            if((sum+nums[i]==0) & (sum-nums[i]==0)) {
                return 2;
            }
            return (sum+nums[i]==0) | (sum-nums[i]==0);
        }
        if(dp.find({i,sum})!=dp.end()){
            return dp[{i,sum}];
        }

        int add = solve(nums,i-1,sum+nums[i],dp);
        int sub = solve(nums,i-1,sum-nums[i],dp);

        return dp[{i,sum}] = sub+add;
    }

public:
    int findTargetSumWays(vector<int>& nums, int target) {
        int n = nums.size();

        // // Recursive
        // return solve(nums,n-1,target);

        // Memoization
        map<pair<int,int>,int> dp;
        return solve(nums,n-1,target,dp);
    }
};

int main() {
    return 0;
}