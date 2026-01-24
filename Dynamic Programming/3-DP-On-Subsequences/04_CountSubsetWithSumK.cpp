#include <bits/stdc++.h>
using namespace std;

class Solution {
    int solve(vector<int> &arr,int i,int sum){
        if(i==0){
            return sum==0;
        }

        int ntake = solve(arr,i-1,sum);
        if(sum>=arr[i-1]){
            int take = solve(arr,i-1,sum-arr[i-1]);
            ntake += take;
        }
        return ntake;
    }

    int solve(vector<int> &arr,int i,int sum, vector<vector<int>> &dp){
        if(i==0){
            return sum==0;
        }
        if(dp[i][sum]!=-1)  return dp[i][sum];

        int ntake = solve(arr,i-1,sum,dp);
        if(sum>=arr[i-1]){
            int take = solve(arr,i-1,sum-arr[i-1],dp);
            ntake += take;
        }
        return dp[i][sum] = ntake;
    }
  public:
    int perfectSum(vector<int>& arr, int target) {
        int n = arr.size();

        // // Recursive
        // return solve(arr,n,target);

        // // Memoization
        // vector<vector<int>> dp(n+1,vector<int> (target+1,-1));
        // return solve(arr,n,target,dp);

        // // Tabulation
        // vector<vector<int>> dp(n+1,vector<int> (target+1,0));
        // dp[0][0] = 1;

        // for(int i=1;i<=n;i++){
        //     for(int sum=0;sum<=target;sum++){
        //         int ntake = dp[i-1][sum];
        //         if(sum>=arr[i-1]){
        //             int take = dp[i-1][sum-arr[i-1]];
        //             ntake += take;
        //         }
        //         dp[i][sum] = ntake;
        //     }
        // }
        // return dp[n][target];

        // Space Optimization
        vector<int> prev(target+1,0), curr(target+1,0);
        prev[0] = 1;

        for(int i=1;i<=n;i++){
            for(int sum=0;sum<=target;sum++){
                int ntake = prev[sum];
                if(sum>=arr[i-1]){
                    int take = prev[sum-arr[i-1]];
                    ntake += take;
                }
                curr[sum] = ntake;
            }
            prev = curr;
        }
        return prev[target];
    }
};

int main() {
    return 0;
}