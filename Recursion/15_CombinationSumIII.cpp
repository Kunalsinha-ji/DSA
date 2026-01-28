#include <bits/stdc++.h>
using namespace std;

class Solution {
    void solve(int sum,int k,int i,vector<int> v,vector<vector<int>> &ans){
        if(sum==0){
            if(k==0){
                ans.push_back(v);
            }
            return;
        }
        if(i>9 || k<0){
            return;
        }

        solve(sum,k,i+1,v,ans);
        if(sum>=i){
            v.push_back(i);
            solve(sum-i,k-1,i+1,v,ans);
            v.pop_back();
        }
    }
public:
    vector<vector<int>> combinationSum3(int k, int n) {
        vector<vector<int>> ans;
        vector<int> v;
        solve(n,k,1,v,ans);
        return ans;
    }
};

int main() {
    return 0;
}