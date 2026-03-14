#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    bool canJump(vector<int>& nums) {
        int n = nums.size();
        int maxJumps = 0;

        for(int i=0;i<n;i++){
            if(maxJumps>=n){
                return true;
            }
            if(maxJumps<i){
                return false;
            }
            maxJumps = max(maxJumps, i + nums[i]);
        }
        return true;
    }
};

int main() {
    return 0;
}