#include <bits/stdc++.h>
using namespace std;

class Solution {
    int solve(vector<int> &coins,int amt, int i){
        if(i==0){
            if(amt%coins[i]==0){
                return 1;
            }
            else{
                return 0;
            }
        }
        if(amt==0){
            return 1;
        }

        int ntake = solve(coins,amt,i-1);
        if(amt>=coins[i]){
            int take = solve(coins,amt-coins[i],i);
            ntake += take;
        }
        return ntake;
    }
    int solve(vector<int> &coins,int amt, int i, vector<vector<int>> &dp){
        if(i==0){
            if(amt%coins[i]==0){
                return 1;
            }
            else{
                return 0;
            }
        }
        if(amt==0){
            return 1;
        }
        if(dp[i][amt]!=-1)  return dp[i][amt];

        int ntake = solve(coins,amt,i-1,dp);
        if(amt>=coins[i]){
            int take = solve(coins,amt-coins[i],i,dp);
            ntake += take;
        }
        return dp[i][amt] = ntake;
    }
public:
    int change(int amount, vector<int>& coins) {
        int n = coins.size();

        // // Recursive
        // return solve(coins,amount,n-1);

        // // Memoization
        // vector<vector<int>> dp(n,vector<int> (amount+1,-1));
        // return solve(coins,amount,n-1,dp);

        // // Tabulation
        // vector<vector<int>> dp(n,vector<int> (amount+1,0));
        // for(int i=0;i<n;i++){
        //     dp[i][0] = 1;
        // }
        // for(int amt=1;amt<=amount;amt++){
        //     if(amt%coins[0]==0){
        //         dp[0][amt] = 1;
        //     }
        // }

        // for(int i=1;i<n;i++){
        //     for(int amt=0;amt<=amount;amt++){
        //         int ntake = dp[i-1][amt];
        //         if(amt>=coins[i]){
        //             int take = dp[i][amt-coins[i]];
        //             ntake += take;
        //         }
        //         dp[i][amt] = ntake;
        //     }
        // }
        // return dp[n-1][amount];

        // Space optimization
        vector<int> prev(amount+1,0), curr(amount+1,0);
        prev[0] = curr[0] = 1;

        for(int amt=1;amt<=amount;amt++){
            if(amt%coins[0]==0){
                prev[amt] = 1;
            }
        }

        for(int i=1;i<n;i++){
            for(int amt=0;amt<=amount;amt++){
                if(amt==0){
                    curr[amt] = 1;
                    continue;
                }
                int ntake = prev[amt];
                if(amt>=coins[i]){
                    int take = curr[amt-coins[i]];
                    ntake += take;
                }
                curr[amt] = ntake;
            }
            prev = curr;
        }
        return prev[amount];
    }
};

int main() {
    return 0;
}