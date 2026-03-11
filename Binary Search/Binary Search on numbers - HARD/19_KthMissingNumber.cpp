#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int findKthPositive(vector<int>& arr, int k) {
        int n = arr.size();

        for(int i=0;i<n;i++){
            if(arr[i]<=k){
                k++;
            }
            else{
                break;
            }
        }

        return k;
    }
};

class Solution {
public:
    int findKthPositive(vector<int>& arr, int k) {
        int n = arr.size();

        int low = 0, high = n-1;

        while(low<=high){
            int mid = low + (high-low)/2;

            int missing = arr[mid] - mid - 1;

            if(missing<k){
                low = mid + 1;
            }
            else{
                high = mid - 1;
            }
        }

        // Now the missing element will be between high - low
        /*
        missing till high = arr[high] - high - 1
        missing element we need to find is after high -> arr[high] + more
        left missing element after high = more = k - missing till high
        therefore missing element we need to find is = arr[high] + k - missing till high
        missing element = arr[high] + k - (arr[high] - high - 1)
        missing element = arr[high] + k - arr[high] + high + 1
        */

        return k + high + 1;
    }
};

int main() {
    return 0;
}