#include <bits/stdc++.h>
using namespace std;

int solve(vector<int> &arr,int i,int k){
    if(i==0){
        return 0;
    }

    int ans = 1e9;
    for(int ind=1;ind<=k;ind++){
        if(i-ind>=0){
            int go = solve(arr,i-ind,k) + abs(arr[i]-arr[i-ind]);
            ans = min(ans,go);
        }
    }
    return ans;
}

int solveMem(vector<int> &arr,int i,int k,vector<int> &dp){
    if(i==0){
        return 0;
    }
    if(dp[i]!=-1)   return dp[i];
    int ans = 1e9;
    for(int ind=1;ind<=k;ind++){
        if(i-ind>=0){
            int go = solveMem(arr,i-ind,k,dp) + abs(arr[i]-arr[i-ind]);
            ans = min(ans,go);
        }
    }
    return dp[i] = ans;
}

int minimizeCost(int n, int k, vector<int> &height){
    // recursive
    // return solve(height,n-1,k);

    // Memoization
    // vector<int> dp(n,-1);
    // return solveMem(height,n-1,k,dp);

    // Tabulation
    vector<int> dp(n,1e9);
    dp[0] = 0;

    for(int i=1;i<n;i++){
        int ans = 1e9;
        for(int ind=1;ind<=k;ind++){
            if(i-ind>=0){
                int go = dp[i-ind] + abs(height[i]-height[i-ind]);
                ans = min(ans,go);
            }
        }
        dp[i] = ans;
    }
    return dp[n-1];
}

int main() {
    return 0;
}