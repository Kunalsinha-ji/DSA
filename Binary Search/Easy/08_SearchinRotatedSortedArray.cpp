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
                return mid;
            }
            // Identify the sorted half
            if(arr[mid]>=arr[low]){
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
        return -1;
    }
};

int main() {
    return 0;
}