#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int removeDuplicates(vector<int>& nums) {
        int n = nums.size();
        int i = 0;
        int j = 1;

        while(j<n){
            if(nums[j]==nums[i]){
                j++;
            }
            else{
                nums[++i] = nums[j];
                j++;
            }
        }
        return i+1;
    }
};

int main() {
    return 0;
}