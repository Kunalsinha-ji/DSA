#include <bits/stdc++.h>
using namespace std;

class Solution {
    int lowerBound(vector<int>& arr, int target) {
        int n = arr.size();
        int ans = n;

        int low = 0, high = n-1;

        while(low<=high){
            int mid = low + (high-low)/2;

            if(arr[mid]>=target){
                ans = mid;
                high = mid - 1;
            }
            else{
                low = mid + 1;
            }
        }
        return ans;
    }
public:
    int searchInsert(vector<int>& nums, int target) {
        return lowerBound(nums,target);
    }
};

int main() {
    return 0;
}