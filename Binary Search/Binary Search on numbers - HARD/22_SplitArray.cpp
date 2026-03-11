#include <bits/stdc++.h>
using namespace std;

class Solution {
    int countSplit(vector<int> &arr,int maxSum){
        int subArr = 1;
        int sum = 0;
        for(auto it: arr){
            if(sum+it>maxSum){
                subArr++;
                sum = it;
            }
            else{
                sum += it;
            }
        }
        return subArr;
    }
public:
    int splitArray(vector<int>& nums, int k) {
        int low = *max_element(nums.begin(),nums.end());
        int high = 0;

        for(auto it: nums){
            high += it;
        }
        int ans = -1;
        while(low<=high){
            int mid = low + (high-low)/2;

            int subArrays = countSplit(nums,mid);

            if(subArrays>k){
                low = mid + 1;
            }
            else{
                high = mid - 1;
            }
        }
        return low;
    }
};

int main() {
    return 0;
}