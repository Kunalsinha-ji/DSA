#include <bits/stdc++.h>
using namespace std;

class Solution {
    void solve(vector<vector<int>> &ans,int i,vector<int> v,int k,int n){
        if(n==0){
            if(v.size()==k){
                ans.push_back(v);
            }
            return;
        }
        if(i==10){
            return;
        }
        if(v.size()>k){
            return;
        }

        solve(ans,i+1,v,k,n);
        if(n>=i){
            v.push_back(i);
            solve(ans,i+1,v,k,n-i);
            v.pop_back();
        }
    }
public:
    vector<vector<int>> combinationSum3(int k, int n) {
        vector<vector<int>> ans;
        solve(ans,1,{},k,n);
        return ans;
    }
};

int main() {
    return 0;
}