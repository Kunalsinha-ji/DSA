#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int minimumDifference(vector<int>& nums) {
        int n = nums.size();
        int sum = 0;

        for(auto it: nums){
            sum += it;
        }

        vector<vector<bool>> dp(n,vector<bool> (sum+1,0));

        for(int i=0;i<n;i++){
            dp[i][0] = true;
        }

        for(int s=0;s<=sum;s++){
            if(nums[0]==s){
                dp[0][s] = true;
            }
        }

        for(int i=1;i<n;i++){
            for(int s=0;s<=sum;s++){
                bool res = false;
                bool ntake = dp[i-1][s];
                if(s>=nums[i]){
                    bool take = dp[i-1][s-nums[i]];
                    res = res | take;
                }
                res = res | ntake;
                dp[i][s] = res;
            }
        }

        int res = 1e9;
        for(int i=0;i<=sum;i++){
            if(dp[n-1][i]==1){
                int s1 = i;
                int s2 = sum-i;
                int diff = abs(s2-s1);
                res = min(res,diff);
            }
        }
        return res;
    }
};

int main() {
    return 0;
}