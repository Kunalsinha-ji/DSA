#include <bits/stdc++.h>
using namespace std;

class Solution {
    void solve(vector<string> &ans,string s,int o,int c){
        if(o==0 && c==0){
            ans.push_back(s);
            return;
        }

        if (o>0 || o==c){
            solve(ans,s+'(',o-1,c);
        }

        if (o<c){
            solve(ans,s+')',o,c-1);
        }
    }
public:
    vector<string> generateParenthesis(int n) {
        vector<string> ans;
        string st = "";
        solve(ans,st,n,n);
        return ans;
    }
};

int main() {
    return 0;
}