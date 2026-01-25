#include <bits/stdc++.h>
using namespace std;

class Solution {
    void solve(vector<vector<int>> &dp,int i,int j,set<string> &ans, string st, string s1, string s2){
        if(i==0 || j==0){
            ans.insert(st);
            return;
        }

        if(s1[i-1]==s2[j-1]){
            st = s1[i-1] + st;
            solve(dp,i-1,j-1,ans,st,s1,s2);
        }
        else{
            if(dp[i-1][j]>dp[i][j-1]){
                solve(dp,i-1,j,ans,st,s1,s2);
            }
            else if(dp[i-1][j]<dp[i][j-1]){
                solve(dp,i,j-1,ans,st,s1,s2);
            }
            else{
                solve(dp,i,j-1,ans,st,s1,s2);
                solve(dp,i-1,j,ans,st,s1,s2);
            }
        }
    }
  public:
    vector<string> allLCS(string &s1, string &s2) {
        int n = s1.size();
        int m = s2.size();

        vector<vector<int>> dp(n+1,vector<int> (m+1,0));

        for(int i=1;i<=n;i++){
            for(int j=1;j<=m;j++){
                if(s1[i-1]==s2[j-1]){
                    dp[i][j] = 1 + dp[i-1][j-1];
                }
                else{
                    dp[i][j] = max(dp[i-1][j],dp[i][j-1]);
                }
            }
        }

        set<string> ans;
        solve(dp,n,m,ans,"",s1,s2);
        vector<string> res;
        for(auto it : ans){
            res.push_back(it);
        }
        return res;
    }
};


int main() {
    return 0;
}