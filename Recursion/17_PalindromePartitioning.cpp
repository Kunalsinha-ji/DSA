#include <bits/stdc++.h>
using namespace std;

class Solution {
    bool isPalindrome(string &s,int i,int j){
        while(i<j){
            if(s[i]!=s[j]){
                return 0;
            }
            i++;
            j--;
        }
        return 1;
    }
    void solve(vector<vector<string>> &ans,string &s,vector<string> v,int i){
        if(i==s.size()){
            ans.push_back(v);
            return;
        }

        string str = "";
        int k = i;
        while(k<s.size()){
            str += s[k];
            if(isPalindrome(s,i,k)){
                v.push_back(str);
                solve(ans,s,v,k+1);
                v.pop_back();
            }
            k++;
        }
    }
public:
    vector<vector<string>> partition(string s) {
        vector<vector<string>> ans;
        solve(ans,s,{},0);
        return ans;
    }
};

int main() {
    return 0;
}