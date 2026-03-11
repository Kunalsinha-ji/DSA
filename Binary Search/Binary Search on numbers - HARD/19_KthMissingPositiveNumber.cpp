#include <bits/stdc++.h>
using namespace std;

// O(N) solution
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

// O(log N)
class Solution {
public:
    int findKthPositive(vector<int>& arr, int k) {
        int n = arr.size();

        int low = 0, high = n-1;

        while(low<=high){
            int mid = low + (high-low)/2;

            int missing = arr[mid] - mid - 1;
            // At index 0 -> 1, 1 -> 2, 2 -> 3 .....

            if(missing<k){
                low = mid + 1;
            }
            else{
                high = mid - 1;
            }
        }

        // Now between high - low we will have our missing number
        // missing before high: arr[high] - high -1;
        // How many missing left -> k - missing before
        // Our answer is -> arr[high] + missing left
        // arr[high] + k - missing
        return k + high + 1;
    }
};
int main() {
    return 0;
}