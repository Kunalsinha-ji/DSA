#include <bits/stdc++.h>
using namespace std;

class Solution {
    int solve(vector<int> &coins,int i,int amt){
        if(amt==0){
            return 0;
        }
        if(i==0){
            if(amt%coins[0]==0){
                return amt/coins[0];
            }
            else{
                return 1e9;
            }
        }

        int ntake = solve(coins,i-1,amt);
        if(amt>=coins[i]){
            int take = solve(coins,i,amt-coins[i]);
            if(take!=1e9){
                take = take + 1;
            }
            ntake = min(take,ntake);
        }
        return ntake;
    }

    int solve(vector<int> &coins,int i,int amt, vector<vector<int>> &dp){
        if(amt==0){
            return 0;
        }
        if(i==0){
            if(amt%coins[0]==0){
                return amt/coins[0];
            }
            else{
                return 1e9;
            }
        }
        if(dp[i][amt]!=-1)  return dp[i][amt];

        int ntake = solve(coins,i-1,amt,dp);
        if(amt>=coins[i]){
            int take = solve(coins,i,amt-coins[i],dp);
            if(take!=1e9){
                take = take + 1;
            }
            ntake = min(take,ntake);
        }
        return dp[i][amt] = ntake;
    }
public:
    int coinChange(vector<int>& coins, int amount) {
        int n = coins.size();

        // Recursive
        // int res = solve(coins,n-1,amount);
        // return res==1e9? -1 : res;

        // // Memoization
        // vector<vector<int>> dp(n,vector<int> (amount+1,-1));
        // int res = solve(coins,n-1,amount,dp);
        // return res==1e9? -1 : res;

        // // Tabulation
        // vector<vector<int>> dp(n,vector<int> (amount+1,1e9));

        // for(int i=0;i<n;i++){
        //     dp[i][0] = 0;
        // }

        // for(int amt=1;amt<=amount;amt++){
        //     if(amt%coins[0]==0){
        //         dp[0][amt] = amt/coins[0];
        //     }
        // }

        // for(int i=1;i<n;i++){
        //     for(int amt=0;amt<=amount;amt++){
        //         int ntake = dp[i-1][amt];
        //         if(amt>=coins[i]){
        //             int take = dp[i][amt-coins[i]];
        //             if(take!=1e9){
        //                 take = take + 1;
        //             }
        //             ntake = min(take,ntake);
        //         }
        //         dp[i][amt] = ntake;
        //     }
        // }
        // return dp[n-1][amount]==1e9? -1: dp[n-1][amount];


        // Space optimization
        vector<int> prev(amount+1,1e9), curr(amount+1,1e9);
        prev[0] = 0, curr[0] = 0;

        for(int amt=1;amt<=amount;amt++){
            if(amt%coins[0]==0){
                prev[amt] = amt/coins[0];
            }
        }

        for(int i=1;i<n;i++){
            for(int amt=0;amt<=amount;amt++){
                if(amt==0){
                    curr[amt] = 0;
                    continue;
                }
                int ntake = prev[amt];
                if(amt>=coins[i]){
                    int take = curr[amt-coins[i]];
                    if(take!=1e9){
                        take = take + 1;
                    }
                    ntake = min(take,ntake);
                }
                curr[amt] = ntake;
            }
            prev = curr;
        }
        return prev[amount]==1e9? -1: prev[amount];
    }
};

int main() {
    return 0;
}