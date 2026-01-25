#include <bits/stdc++.h>
using namespace std;

void solve(vector<int> &nums,vector<vector<int>> &ans,vector<int> v,int sum,int i){
    if(sum==0){
        ans.push_back(v);
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
vector<vector<int>> subsequences(vector<int> &nums,int sum){
    vector<vector<int>> ans;
    solve(nums,ans,{},sum,0);
    return ans;
}

int main() {

    return 0;
}