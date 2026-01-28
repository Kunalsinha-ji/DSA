#include <bits/stdc++.h>
using namespace std;

class Solution {
    void solve(string &digits,int i,unordered_map<char,string> &mp,string s,vector<string> &ans){
        if(i==digits.size()){
            ans.push_back(s);
            return;
        }

        string word = mp[digits[i]];

        for(int k=0;k<word.size();k++){
            s += word[k];
            solve(digits,i+1,mp,s,ans);
            s.pop_back();
        }
    }
public:
    vector<string> letterCombinations(string digits) {
        vector<string> ans;
        string st = "";
        unordered_map<char,string> mp;
        mp['2'] = "abc";
        mp['3'] = "def";
        mp['4'] = "ghi";
        mp['5'] = "jkl";
        mp['6'] = "mno";
        mp['7'] = "pqrs";
        mp['8'] = "tuv";
        mp['9'] = "wxyz";

        solve(digits,0,mp,st,ans);
        return ans;
    }
};

int main() {
    return 0;
}