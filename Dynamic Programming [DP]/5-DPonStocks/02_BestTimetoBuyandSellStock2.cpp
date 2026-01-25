#include <bits/stdc++.h>
using namespace std;

class Solution {
    int solve(vector<int> &prices, int i, bool buy){
        if(i==prices.size()){
            return 0;
        }

        if(buy){
            int take = solve(prices,i+1,!buy) - prices[i];
            int ntake = solve(prices,i+1,buy);

            return max(take,ntake);
        }
        else{
            int sell = solve(prices,i+1,!buy) + prices[i];
            int nsell = solve(prices,i+1,buy);

            return max(sell,nsell);
        }
    }
    int solve(vector<int> &prices, int i, bool buy, vector<vector<int>> &dp){
        if(i==prices.size()){
            return 0;
        }
        if(dp[i][buy]!=-1)  return dp[i][buy];

        if(buy){
            int take = solve(prices,i+1,!buy,dp) - prices[i];
            int ntake = solve(prices,i+1,buy,dp);

            return dp[i][buy] = max(take,ntake);
        }
        else{
            int sell = solve(prices,i+1,!buy,dp) + prices[i];
            int nsell = solve(prices,i+1,buy,dp);

            return dp[i][buy] = max(sell,nsell);
        }
    }
public:
    int maxProfit(vector<int>& prices) {
        int n = prices.size();

        // // Recursive
        // return solve(prices,0,1);

        // // Memoization
        // vector<vector<int>> dp(n,vector<int> (2,-1));
        // return solve(prices,0,1,dp);

        // // Tabulation
        // vector<vector<int>> dp(n+1,vector<int> (2,0));

        // for(int i=n-1;i>=0;i--){
        //     for(int buy=0;buy<=1;buy++){
        //         if(buy){
        //             int take = dp[i+1][!buy] - prices[i];
        //             int ntake = dp[i+1][buy];

        //             dp[i][buy] = max(take,ntake);
        //         }
        //         else{
        //             int sell = dp[i+1][!buy] + prices[i];
        //             int nsell = dp[i+1][buy];

        //             dp[i][buy] = max(sell,nsell);
        //         }
        //     }
        // }
        // return dp[0][1];

        // Space optimization
        // Tabulation
        vector<int> prev(2,0) ,curr (2,0);

        for(int i=n-1;i>=0;i--){
            for(int buy=0;buy<=1;buy++){
                if(buy){
                    int take = prev[!buy] - prices[i];
                    int ntake = prev[buy];

                    curr[buy] = max(take,ntake);
                }
                else{
                    int sell = prev[!buy] + prices[i];
                    int nsell = prev[buy];

                    curr[buy] = max(sell,nsell);
                }
            }
            prev = curr;
        }
        return prev[1];
    }
};

int main() {
    return 0;
}