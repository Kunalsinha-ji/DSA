#include <bits/stdc++.h>
using namespace std;

class Solution {
  public:
    int findKRotation(vector<int> &arr) {
        int n = arr.size();
        int ind = 0;
        int ans = INT_MAX;

        int low = 0, high = n-1;

        while(low<=high){
            int mid = low + (high-low)/2;

            // Find sorted half
            if(arr[mid]>=arr[low]){
                // Left sorted
                if(ans>arr[low]){
                    ans = min(ans,arr[low]);
                    ind = low;
                }
                low = mid + 1;
            }
            else{
                // Right sorted
                if(ans>arr[mid]){
                    ans = min(ans,arr[mid]);
                    ind = mid;
                }
                high = mid - 1;
            }
        }
        return ind;
    }
};


int main() {
    return 0;
}