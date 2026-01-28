#include <bits/stdc++.h>
using namespace std;

class Solution {
    void solve(vector<string> &ans,string st,int n){
        if(n==0){
            ans.push_back(st);
            return;
        }

        solve(ans,st+"0",n-1);
        solve(ans,st+"1",n-1);
    }
  public:
    vector<string> binstr(int n) {
        vector<string> ans;
        string st = "";
        solve(ans,st,n);
        return ans;
    }
};

int main() {
    return 0;
}