#include <bits/stdc++.h>
using namespace std;

class Solution {
    void solve(vector<string> &ans,string s,int n){
        if(n==0){
            ans.push_back(s);
            return;
        }
        solve(ans,s+"0",n-1);
        solve(ans,s+"1",n-1);
    }
  public:
    vector<string> binstr(int n) {
        vector<string> ans;
        solve(ans,"",n);
        return ans;
    }
};

int main() {
    return 0;
}