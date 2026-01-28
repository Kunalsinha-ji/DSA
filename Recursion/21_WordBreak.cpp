#include <bits/stdc++.h>
using namespace std;

class Solution {
    bool solve(string &s,set<string> &st,int i){
        if(i==s.size()){
            return 1;
        }

        string str = "";
        for(int k=i;k<s.size();k++){
            str += s[k];
            if(st.find(str)!=st.end()){
                bool res = solve(s,st,k+1);
                if(res){
                    return 1;
                }
            }
        }
        return 0;
    }
public:
    bool wordBreak(string s, vector<string>& wordDict) {
        set<string> st(wordDict.begin(),wordDict.end());
        return solve(s,st,0);
    }
};

class Solution {
    bool solve(string &s,set<string> &st,int i,vector<int> &dp){
        if(i==s.size()){
            return 1;
        }
        if(dp[i]!=-1)   return dp[i];

        string str = "";
        for(int k=i;k<s.size();k++){
            str += s[k];
            if(st.find(str)!=st.end()){
                bool res = solve(s,st,k+1,dp);
                if(res){
                    return dp[i] =  1;
                }
            }
        }
        return dp[i] = 0;
    }
public:
    bool wordBreak(string s, vector<string>& wordDict) {
        set<string> st(wordDict.begin(),wordDict.end());
        vector<int> dp(s.size(),-1);
        return solve(s,st,0,dp);
    }
};

int main() {
    return 0;
}