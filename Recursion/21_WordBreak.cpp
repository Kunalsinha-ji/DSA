#include <bits/stdc++.h>
using namespace std;

class Solution {
    bool solve(string &s,set<string> &words, int i){
        if(i==s.size()){
            return 1;
        }

        string word = "";
        for(int k=i;k<s.size();k++){
            word += s[k];
            if(words.find(word)!=words.end()){
                bool res = solve(s,words,k+1);
                if(res){
                    return 1;
                }
            }
        }
        return 0;
    }

    bool solve(string &s,set<string> &words, int i,vector<int> &dp){
        if(i==s.size()){
            return 1;
        }
        if(dp[i]!=-1)   return dp[i];

        string word = "";
        for(int k=i;k<s.size();k++){
            word += s[k];
            if(words.find(word)!=words.end()){
                bool res = solve(s,words,k+1,dp);
                if(res){
                    return dp[i] = 1;
                }
            }
        }
        return dp[i] = 0;
    }
public:
    bool wordBreak(string s, vector<string>& wordDict) {
        set<string> words(wordDict.begin(),wordDict.end());

        // // Recursive
        // return solve(s,words,0);

        // Memoization
        vector<int> dp(s.size(),-1);
        return solve(s,words,0,dp);
    }
};

int main() {
    return 0;
}