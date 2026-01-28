#include <bits/stdc++.h>
using namespace std;

class Solution {
    void solve(vector<string> &ans,string st,int o,int c){
        if(o==0 && c==0){
            ans.push_back(st);
            return;
        }

        if(o || o==c){
            solve(ans,st+"(",o-1,c);
        }
        if(c>o){
            solve(ans,st+")",o,c-1);
        }
    }
public:
    vector<string> generateParenthesis(int n) {
        vector<string> ans;
        solve(ans,"",n,n);
        return ans;
    }
};

int main() {
    return 0;
}