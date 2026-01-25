#include <bits/stdc++.h>
using namespace std;

class Solution {
    bool solve(string &s,string &p,int i,int j){
        if(i==0 && j==0){
            return 1;
        }
        if(i==0){
            while(j>0){
                if(p[j-1]!='*'){
                    return 0;
                }
                j--;
            }
            return 1;
        }
        if(j==0){
            return 0;
        }

        if(s[i-1]==p[j-1] || p[j-1]=='?'){
            return solve(s,p,i-1,j-1);
        }
        else if(p[j-1]=='*'){
            int skip = solve(s,p,i,j-1);
            int match = solve(s,p,i-1,j-1);
            int match2 = solve(s,p,i-1,j);
            return skip | match | match2;
        }
        else{
            return 0;
        }
    }
    bool solve(string &s,string &p,int i,int j,vector<vector<int>> &dp){
        if(i==0 && j==0){
            return 1;
        }
        if(i==0){
            while(j>0){
                if(p[j-1]!='*'){
                    return 0;
                }
                j--;
            }
            return 1;
        }
        if(j==0){
            return 0;
        }
        if(dp[i][j]!=-1)    return dp[i][j];

        if(s[i-1]==p[j-1] || p[j-1]=='?'){
            return dp[i][j] = solve(s,p,i-1,j-1,dp);
        }
        else if(p[j-1]=='*'){
            int skip = solve(s,p,i,j-1,dp);
            int match = solve(s,p,i-1,j-1,dp);
            int match2 = solve(s,p,i-1,j,dp);
            return dp[i][j] = skip | match | match2;
        }
        else{
            return dp[i][j] = 0;
        }
    }
public:
    bool isMatch(string s, string p) {
        int n = s.size();
        int m = p.size();

        // // Recursive
        // return solve(s,p,n,m);

        // // Memoization
        // vector<vector<int>> dp(n+1,vector<int> (m+1,-1));
        // return solve(s,p,n,m,dp);

        // Tabulation
        vector<vector<int>> dp(n+1,vector<int> (m+1,0));
        dp[0][0] = 1;
        for(int jj=1;jj<=m;jj++){
            int j = jj;
            while(j>0){
                if(p[j-1]!='*'){
                    break;
                }
                j--;
            }
            if(j==0){
                dp[0][jj] = 1;
            }
        }

        for(int i=1;i<=n;i++){
            for(int j=1;j<=m;j++){
                if(s[i-1]==p[j-1] || p[j-1]=='?'){
                    dp[i][j] = dp[i-1][j-1];
                }
                else if(p[j-1]=='*'){
                    int skip = dp[i][j-1];
                    int match = dp[i-1][j-1];
                    int match2 = dp[i-1][j];
                    dp[i][j] = skip | match | match2;
                }
                else{
                    dp[i][j] = 0;
                }
            }
        }
        return dp[n][m];
    }
};

int main() {
    return 0;
}