#include <bits/stdc++.h>
using namespace std;

class Solution {
    bool isPalindrome(string &s,int i,int j){
        while(i<j){
            if(s[i]!=s[j]){
                return 0;
            }
            i++;j--;
        }
        return 1;
    }
    void solve(string &s,int i,vector<string> v,vector<vector<string>> &ans){
        if(i==s.size()){
            ans.push_back(v);
            return;
        }

        string str = "";
        for(int k=i;k<s.size();k++){
            str += s[k];
            if(isPalindrome(s,i,k)){
                v.push_back(str);
                solve(s,k+1,v,ans);
                v.pop_back();
            }
        }
    }
public:
    vector<vector<string>> partition(string s) {
        vector<vector<string>> ans;
        vector<string> v;
        solve(s,0,v,ans);
        return ans;
    }
};

int main() {
    return 0;
}