#include <bits/stdc++.h>
using namespace std;

class Solution {
    void solve(vector<int> &nums,set<vector<int>> &ans,vector<int> v,int sum,int i){
    if(sum==0){
        ans.insert(v);
        return;
    }
    if(i==nums.size()){
        return;
    }

    solve(nums,ans,v,sum,i+1);
    if(sum>=nums[i]){
        v.push_back(nums[i]);
        solve(nums,ans,v,sum-nums[i],i+1);
        v.pop_back();
    }
}
public:
    vector<vector<int>> combinationSum2(vector<int>& candidates, int target) {
        sort(candidates.begin(),candidates.end());
        set<vector<int>> ans;
        solve(candidates,ans,{},target,0);
        vector<vector<int>> res;
        for(auto it: ans){
            res.push_back(it);
        }
        return res;
    }
};

int main() {
    return 0;
}