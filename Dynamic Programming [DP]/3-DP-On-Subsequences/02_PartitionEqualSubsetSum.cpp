#include <bits/stdc++.h>
using namespace std;

class Solution {
    bool solve(vector<int> &nums,int size,int sum){
        vector<bool> prev(sum+1,0), curr(sum+1,0);

        prev[0] = true;
        if(nums[0]<=sum){
            prev[nums[0]] = true;
        }

        for(int i=1;i<size;i++){
            for(int s=0;s<=sum;s++){
                bool res = false;
                bool ntake = prev[s];
                if(s>=nums[i]){
                    bool take = prev[s-nums[i]];
                    res = res | take;
                }
                res = res | ntake;
                curr[s] = res;
            }
            prev = curr;
        }
        return prev[sum];
    }
public:
    bool canPartition(vector<int>& nums) {
        int sum = 0;
        int n = nums.size();

        for(auto it: nums){
            sum += it;
        }
        if(sum%2){
            return 0;
        }

        return solve(nums,n,sum/2);
    }
};

int main() {
    return 0;
}