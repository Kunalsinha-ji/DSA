#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    vector<vector<int>> subsetsWithDup(vector<int>& nums) {
        int n = nums.size();
        n = pow(2,n);

        set<vector<int>> res;
        sort(nums.begin(),nums.end());

        for(int i=0;i<n;i++){
            int num = i;
            int ind = 0;
            vector<int> v;
            while(num){
                if(num&1){
                    v.push_back(nums[ind]);
                }
                num = num>>1;
                ind++;
            }
            res.insert(v);
        }

        vector<vector<int>> ans;
        for(auto it: res){
            ans.push_back(it);
        }
        return ans;
    }
};

int main() {
    return 0;
}