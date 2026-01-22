#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    void sortColors(vector<int>& nums) {
        int n = nums.size();
        int i = 0,k=n-1, j=0;

        while(i<=k && j<=k){
            if(nums[j]==2){
                swap(nums[j],nums[k]);
                k--;
            }
            else if(nums[j]==0){
                swap(nums[i],nums[j]);
                i++;
                j++;
            }
            else{
                j++;
            }
        }
    }
};

int main() {
    return 0;
}