#include <bits/stdc++.h>
using namespace std;

class Solution {
    int firstOccurence(vector<int> &arr,int target){
        int n = arr.size();
        int ans = -1;

        int low = 0, high = n-1;

        while(low<=high){
            int mid = low + (high-low)/2;

            if(arr[mid]==target){
                ans = mid;
                high = mid - 1;
            }
            else if(arr[mid]>target){
                high = mid - 1;
            }
            else{
                low = mid + 1;
            }
        }
        return ans;
    }
    int lastOccurence(vector<int> &arr,int target){
        int n = arr.size();
        int ans = -1;

        int low = 0, high = n-1;

        while(low<=high){
            int mid = low + (high-low)/2;

            if(arr[mid]==target){
                ans = mid;
                low = mid + 1;
            }
            else if(arr[mid]>target){
                high = mid - 1;
            }
            else{
                low = mid + 1;
            }
        }
        return ans;
    }
public:
    vector<int> searchRange(vector<int>& nums, int target) {
        int first = firstOccurence(nums,target);
        if(first==-1)   return {-1,-1};
        int last = lastOccurence(nums,target);
        return {first,last};
    }
};

int main() {
    return 0;
}