#include <bits/stdc++.h>
using namespace std;

class Solution {
    void solve(vector<int> &nums,vector<int> v,vector<vector<int>> &ans,int i){
        if(i==nums.size()){
            ans.push_back(v);
            return;
        }

        solve(nums,v,ans,i+1);
        v.push_back(nums[i]);
        solve(nums,v,ans,i+1);
        v.pop_back();
    }
public:
    vector<vector<int>> subsets(vector<int>& nums) {
        vector<vector<int>> ans;
        vector<int> v;
        solve(nums,v,ans,0);
        return ans;
    }
};

class Solution {
public:
    vector<vector<int>> subsets(vector<int>& nums) {
        int n = nums.size();
        vector<vector<int>> ans;

        int k = pow(2,n);

        for(int i=0;i<k;i++){
            int num = i;
            int ind = 0;
            vector<int> temp;
            while(num){
                if(num&1){
                    temp.push_back(nums[ind]);
                }
                num = num>>1;
                ind++;
            }
            ans.push_back(temp);
        }
        return ans;
    }
};

int main() {
    return 0;
}