#include <bits/stdc++.h>
using namespace std;

class Solution {
    void solve(vector<int> &nums,int i,vector<int> v,vector<vector<int>> &ans){
        if(i==nums.size()){
            ans.push_back(v);
            return;
        }

        solve(nums,i+1,v,ans);
        v.push_back(nums[i]);
        solve(nums,i+1,v,ans);
        v.pop_back();
    }
public:
    vector<vector<int>> subsets(vector<int>& nums) {
        vector<vector<int>> ans;
        vector<int> v;
        solve(nums,0,v,ans);
        return ans;
    }
};

class Solution {
public:
    vector<vector<int>> subsets(vector<int>& nums) {
        int n = nums.size();
        n = pow(2,n);

        vector<vector<int>> ans;
        for(int i=0;i<n;i++){
            vector<int> v;
            int num = i;
            int ind = 0;

            while(num){
                if(num&1){
                    v.push_back(nums[ind]);
                }
                num = num>>1;
                ind++;
            }
            ans.push_back(v);
        }
        return ans;
    }
};

int main() {
    return 0;
}