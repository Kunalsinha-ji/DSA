#include <bits/stdc++.h>
using namespace std;

class Solution {
    int solve(int l, int r, vector<int>& nums){
        int last1 = 0;
        int last = nums[l];

        for(int i = l + 1; i <= r; i++){
            int take = last1 + nums[i];
            int ntake = last;
            int curr = max(take, ntake);

            last1 = last;
            last = curr;
        }
        return last;
    }

public:
    int rob(vector<int>& nums) {
        int n = nums.size();
        if(n == 1) return nums[0];

        return max(solve(0, n-2, nums),solve(1, n-1, nums));
    }
};


int main() {
    return 0;
}