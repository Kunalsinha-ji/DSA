#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int jump(vector<int>& nums) {
        int n = nums.size();
        int totalJumps = 0;
        int left = 0, right = 0;

        while(right<n-1){
            int maxJumps = left;  // from this point what is max we can jump
            while(left<=right){
                int jumps = left + nums[left];
                maxJumps = max(jumps,maxJumps);
                left++;
            }
            left = right+1;
            right = maxJumps;
            totalJumps++;
        }
        return totalJumps;
    }
};

int main() {
    return 0;
}