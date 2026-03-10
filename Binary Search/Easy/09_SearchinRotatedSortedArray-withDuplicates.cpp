#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int search(vector<int>& arr, int target) {
        int n = arr.size();
        int low = 0, high = n-1;

        while(low<=high){
            int mid = low + (high-low)/2;

            if(arr[mid]==target){
                return true;
            }
            // Identify the case if mid, low and high have same element
            if(arr[mid]==arr[low] && arr[mid]==arr[high]){
                low++;
                high--;
            }
            // Identify the sorted half
            else if(arr[mid]>=arr[low]){
                // Left sorted
                if(target>=arr[low] && target<=arr[mid]){
                    high = mid - 1;
                }
                else{
                    low = mid + 1;
                }
            }
            else{
                // Right sorted
                if(target>=arr[mid] && target<=arr[high]){
                    low = mid + 1;
                }
                else{
                    high = mid - 1;
                }
            }
        }
        return false;
    }
};


int main() {
    return 0;
}