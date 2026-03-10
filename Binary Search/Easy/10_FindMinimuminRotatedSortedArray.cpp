#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int findMin(vector<int>& arr) {
        int n = arr.size();
        int low = 0, high = n-1;
        int ans = INT_MAX;

        while(low<=high){
            int mid = low + (high-low)/2;

            // This conditions directly checks if sorted array is not rotated
            if(arr[mid]>=arr[low] && arr[mid]<=arr[high]){
                return min(ans,arr[low]);
            }

            // Identify the sorted part
            if(arr[mid]>=arr[low]){
                // Left sorted the select min from left part and go to right
                ans = min(ans,arr[low]);
                low = mid + 1;
            }
            else{
                // Right sorted the select min from right part and go to left
                ans = min(ans,arr[mid]);
                high = mid - 1;
            }
        }
        return ans;
    }
};

int main() {
    return 0;
}