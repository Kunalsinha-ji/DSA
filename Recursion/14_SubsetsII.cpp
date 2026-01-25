#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    vector<vector<int>> subsetsWithDup(vector<int>& nums) {
        sort(nums.begin(),nums.end());
        set<vector<int>> ans;
        int n = nums.size();

        n = pow(2,n);

        for(int i=0;i<n;i++){
            int num = i;
            vector<int> v;
            int j = 0;
            while(num){
                if((num&1)==1){
                    v.push_back(nums[j]);
                }
                j++;
                num = num>>1;
            }
            ans.insert(v);
        }

        vector<vector<int>> res;
        for(auto i : ans){
            res.push_back(i);
        }
        return res;
    }
};

int main() {
    return 0;
}