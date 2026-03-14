#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int jump(vector<int>& nums) {
        int jumps = 0;
        int l = 0, r = 0;

        while(l<nums.size()-1 && r<nums.size()-1){
            int maxJumps = l;
            while(l<=r){
                int jump = l + nums[l];
                maxJumps = max(maxJumps,jump);
                l++;
            }
            l = r + 1;
            r = maxJumps;
            jumps++;
        }
        return jumps;
    }
};

int main() {
    return 0;
}