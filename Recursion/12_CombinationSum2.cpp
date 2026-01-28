#include <bits/stdc++.h>
using namespace std;

class Solution {
    void solve(vector<int> &nums,int i,int sum,vector<int> v,set<vector<int>> &res){
        if(sum==0){
            res.insert(v);
            return;
        }
        if(i==nums.size()){
            return;
        }

        solve(nums,i+1,sum,v,res);
        if(sum>=nums[i]){
            v.push_back(nums[i]);
            solve(nums,i+1,sum-nums[i],v,res);
            v.pop_back();
        }
    }
public:
    vector<vector<int>> combinationSum2(vector<int>& candidates, int target) {
        vector<vector<int>> ans;
        sort(candidates.begin(),candidates.end());
        vector<int> v;
        set<vector<int>> res;
        solve(candidates,0,target,v,res);

        for(auto it: res){
            ans.push_back(it);
        }
        return ans;
    }
};

int main() {
    return 0;
}