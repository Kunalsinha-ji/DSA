#include <bits/stdc++.h>
using namespace std;

class Solution {
    int solve(vector<int> &prices,int i,int cnt){
        if(i==prices.size() || cnt==0){
            return 0;
        }

        if(cnt%2==0){
            int take = solve(prices,i+1,cnt-1) - prices[i];
            int ntake = solve(prices,i+1,cnt);
            return max(take,ntake);
        }
        else{
            int sell = solve(prices,i+1,cnt-1) + prices[i];
            int nsell = solve(prices,i+1,cnt);
            return max(sell,nsell);
        }
    }
    int solve(vector<int> &prices,int i,int cnt, vector<vector<int>> &dp){
        if(i==prices.size() || cnt==0){
            return 0;
        }
        if(dp[i][cnt]!=-1)  return dp[i][cnt];

        if(cnt%2==0){
            int take = solve(prices,i+1,cnt-1,dp) - prices[i];
            int ntake = solve(prices,i+1,cnt,dp);
            return dp[i][cnt] = max(take,ntake);
        }
        else{
            int sell = solve(prices,i+1,cnt-1,dp) + prices[i];
            int nsell = solve(prices,i+1,cnt,dp);
            return dp[i][cnt] = max(sell,nsell);
        }
    }
public:
    int maxProfit(vector<int>& prices) {
        int n = prices.size();

        // // Recursive
        // return solve(prices,0,4);

        // // Memoization
        // vector<vector<int>> dp(n+1,vector<int> (5,-1));
        // return solve(prices,0,4,dp);

        // // Tabulation
        // vector<vector<int>> dp(n+1,vector<int> (5,0));
        // for(int i=n-1;i>=0;i--){
        //     for(int cnt=1;cnt<5;cnt++){
        //         if(cnt%2==0){
        //             int take = dp[i+1][cnt-1] - prices[i];
        //             int ntake = dp[i+1][cnt];
        //             dp[i][cnt] = max(take,ntake);
        //         }
        //         else{
        //             int sell = dp[i+1][cnt-1] + prices[i];
        //             int nsell = dp[i+1][cnt];
        //             dp[i][cnt] = max(sell,nsell);
        //         }
        //     }
        // }
        // return dp[0][4];

        // Space optimization
        vector<int> prev(5,0) ,curr (5,0);
        for(int i=n-1;i>=0;i--){
            for(int cnt=1;cnt<5;cnt++){
                if(cnt%2==0){
                    int take = prev[cnt-1] - prices[i];
                    int ntake = prev[cnt];
                    curr[cnt] = max(take,ntake);
                }
                else{
                    int sell = prev[cnt-1] + prices[i];
                    int nsell = prev[cnt];
                    curr[cnt] = max(sell,nsell);
                }
            }
            prev = curr;
        }
        return prev[4];
    }
};

int main() {
    return 0;
}