#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    void moveZeroes(vector<int>& nums) {
        int n = nums.size();
        int i = -1;int j = 0;
        while(i<n && j<n){
            if(nums[j]!=0){
                i++;
                nums[i] = nums[j];
            }
            j++;
        }
        i++;
        while(i<n){
            nums[i] = 0;
            i++;
        }
    }
};

int main() {
    return 0;
}