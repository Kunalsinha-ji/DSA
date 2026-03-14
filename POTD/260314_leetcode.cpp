#include <bits/stdc++.h>
using namespace std;

/*
https://leetcode.com/problems/the-k-th-lexicographical-string-of-all-happy-strings-of-length-n/?envType=daily-question&envId=2026-03-14
*/

class Solution {
    void solve(vector<string> &ans, string st, int i){
        if(i==0){
            ans.push_back(st);
            return;
        }

        vector<char> ch = {'a','b','c'};

        for(auto it: ch){
            if(st.size()>0 && st.back()==it)    continue;
            st.push_back(it);
            solve(ans,st,i-1);
            st.pop_back();
        }
    }
public:
    string getHappyString(int n, int k) {
        vector<string> ans;
        string st = "";
        solve(ans,st,n);
        if(ans.size()<k){
            return "";
        }
        return ans[k-1];
    }
};

int main() {
    return 0;
}