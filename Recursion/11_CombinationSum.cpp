#include <bits/stdc++.h>
using namespace std;

class Solution {
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
            solve(nums,ans,v,sum-nums[i],i);
            v.pop_back();
        }
    }
public:
    vector<vector<int>> combinationSum(vector<int>& candidates, int target) {
        vector<vector<int>> ans;
        solve(candidates,ans,{},target,0);
        return ans;
    }
};

class Solution {
    void solve(vector<vector<int>> &ans,vector<int> v,vector<int> &arr,int sum,int i){
        if(sum==0){
            ans.push_back(v);
            return;
        }
        if(i<0){
            return;
        }

        solve(ans,v,arr,sum,i-1);
        if(sum>=arr[i]){
            v.push_back(arr[i]);
            solve(ans,v,arr,sum-arr[i],i);
            v.pop_back();
        }
    }
  public:
    vector<vector<int>> targetSumComb(vector<int> &arr, int target) {
        int n = arr.size();
        vector<vector<int>> ans;
        vector<int> v;
        solve(ans,v,arr,target,n-1);
        return ans;
    }
};

int main() {
    return 0;
}