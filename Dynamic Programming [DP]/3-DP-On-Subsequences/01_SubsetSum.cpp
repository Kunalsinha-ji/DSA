#include <bits/stdc++.h>
using namespace std;

class Solution {
    bool solve(vector<int> &arr,int i,int sum){
        if(sum==0){
            return true;
        }
        if(i==0){
            return arr[i]==sum;
        }

        bool res = false;
        bool ntake = solve(arr,i-1,sum);
        if(sum>=arr[i]){
            bool take = solve(arr,i-1,sum-arr[i]);
            res = res | take;
        }
        return res | ntake;
    }

    bool solve(vector<int> &arr,int i,int sum,vector<vector<int>> &dp){
        if(sum==0){
            return true;
        }
        if(i==0){
            return arr[i]==sum;
        }
        if(dp[i][sum]!=-1)  return dp[i][sum];

        bool res = false;
        bool ntake = solve(arr,i-1,sum,dp);
        if(sum>=arr[i]){
            bool take = solve(arr,i-1,sum-arr[i],dp);
            res = res | take;
        }
        return dp[i][sum] = res | ntake;
    }
  public:
    bool isSubsetSum(vector<int>& arr, int sum) {
        int n = arr.size();

        // // Recursive
        // return solve(arr,n-1,sum);

        // // Memoization
        // vector<vector<int>> dp(n,vector<int> (sum+1,-1));
        // return solve(arr,n-1,sum,dp);

        // // Tabulation
        // vector<vector<bool>> dp(n,vector<bool> (sum+1,0));
        // for(int i=0;i<n;i++){
        //     dp[i][0] = true;
        // }

        // for(int s=0;s<=sum;s++){
        //     if(arr[0]==s){
        //         dp[0][s] = true;
        //     }
        // }

        // for(int i=1;i<n;i++){
        //     for(int s=0;s<=sum;s++){
        //         bool res = false;
        //         bool ntake = dp[i-1][s];
        //         if(s>=arr[i]){
        //             bool take = dp[i-1][s-arr[i]];
        //             res = res | take;
        //         }
        //         dp[i][s] = res | ntake;
        //     }
        // }
        // return dp[n-1][sum];

        // Space optimization
        vector<bool> prev(sum+1,0), curr(sum+1,0);
        prev[0] = true;

        if(arr[0]<=sum){
            prev[arr[0]] = true;
        }

        for(int i=1;i<n;i++){
            for(int s=0;s<=sum;s++){
                bool res = false;
                bool ntake = prev[s];
                if(s>=arr[i]){
                    bool take = prev[s-arr[i]];
                    res = res | take;
                }
                curr[s] = res | ntake;
            }
            prev = curr;
        }
        return prev[sum];
    }
};

int main() {
    return 0;
}