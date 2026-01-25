#include <bits/stdc++.h>
using namespace std;

class Solution {
    void solve(vector<string> &ans,string s,unordered_map<int,string> &mp,int i,string &digits){
        if(i==digits.size()){
            ans.push_back(s);
            return;
        }

        string str = mp[digits[i]-'0'];

        for(auto ch: str){
            s += ch;
            solve(ans,s,mp,i+1,digits);
            s.pop_back();
        }
    }
public:
    vector<string> letterCombinations(string digits) {
        vector<string> ans;
        string s = "";
        unordered_map<int,string> mp;
        mp[2] = "abc";
        mp[3] = "def";
        mp[4] = "ghi";
        mp[5] = "jkl";
        mp[6] = "mno";
        mp[7] = "pqrs";
        mp[8] = "tuv";
        mp[9] = "wxyz";

        solve(ans,s,mp,0,digits);
        return ans;
    }
};

int main() {
    return 0;
}