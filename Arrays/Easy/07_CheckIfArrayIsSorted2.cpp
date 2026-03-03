#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    bool check(vector<int>& nums) {
        int n = nums.size();
        int ind = -1;

        for(int i=1;i<n;i++){
            if(nums[i]<nums[i-1]){
                ind = i;
                break;
            }
        }
        if(ind==-1) return true;

        for(int i=ind;i<n+ind-1;i++){
            if(nums[i%n]>nums[(i+1)%n]){
                return false;
            }
        }
        return true;
    }
};

int main() {
    return 0;
}