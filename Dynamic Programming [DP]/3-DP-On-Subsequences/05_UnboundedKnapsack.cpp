#include <bits/stdc++.h>
using namespace std;

class Solution {
    int solve(vector<int> &val,vector<int> &wt, int cap, int i){
        if(cap==0){
            return 0;
        }
        if(i==0){
            return (cap/wt[i]) * val[i];
        }

        int res = 0;
        int ntake = solve(val,wt,cap,i-1);
        if(cap>=wt[i]){
            int take = solve(val,wt,cap-wt[i],i) + val[i];
            res = max(res,take);
        }

        return max(res,ntake);
    }

    int solve(vector<int> &val,vector<int> &wt, int cap, int i, vector<vector<int>> &dp){
        if(cap==0){
            return 0;
        }
        if(i==0){
            return (cap/wt[i]) * val[i];
        }
        if(dp[i][cap]!=-1)  return dp[i][cap];

        int res = 0;
        int ntake = solve(val,wt,cap,i-1,dp);
        if(cap>=wt[i]){
            int take = solve(val,wt,cap-wt[i],i,dp) + val[i];
            res = max(res,take);
        }

        return dp[i][cap] = max(res,ntake);
    }
  public:
    int knapSack(vector<int>& val, vector<int>& wt, int capacity) {
        int n = val.size();

        // // Recursive
        // return solve(val,wt,capacity,n-1);

        // // Memoization
        // vector<vector<int>> dp(n,vector<int> (capacity+1,-1));
        // return solve(val,wt,capacity,n-1,dp);

        // // Tabulation
        // vector<vector<int>> dp(n,vector<int> (capacity+1,0));

        // for(int cap=0;cap<=capacity;cap++){
        //     dp[0][cap] = (cap/wt[0]) * val[0];
        // }

        // for(int i=1;i<n;i++){
        //     for(int cap=0;cap<=capacity;cap++){
        //         int res = 0;
        //         int ntake = dp[i-1][cap];
        //         if(cap>=wt[i]){
        //             int take = dp[i][cap-wt[i]] + val[i];
        //             res = max(res,take);
        //         }

        //         dp[i][cap] = max(res,ntake);
        //     }
        // }
        // return dp[n-1][capacity];

        // Space optimization
        vector<int> prev(capacity+1,0), curr(capacity+1,0);

        for(int cap=0;cap<=capacity;cap++){
            prev[cap] = (cap/wt[0]) * val[0];
        }

        for(int i=1;i<n;i++){
            for(int cap=0;cap<=capacity;cap++){
                int res = 0;
                int ntake = prev[cap];
                if(cap>=wt[i]){
                    int take = curr[cap-wt[i]] + val[i];
                    res = max(res,take);
                }

                curr[cap] = max(res,ntake);
            }
            prev = curr;
        }
        return prev[capacity];
    }
};

int main() {
    return 0;
}