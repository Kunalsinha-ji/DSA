#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int removeDuplicates(vector<int>& nums) {
        int n = nums.size();
        if(nums.size()==1){
            return 1;
        }

        int i=0,j=1;

        while(j<nums.size() && i<nums.size()){
            if(nums[i]==nums[j]){
                j++;
            }
            else{
                nums[++i]= nums[j];
                j++;
            }
        }
        return i+1;
    }
};

int main() {
    return 0;
}