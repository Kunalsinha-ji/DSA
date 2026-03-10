#include <bits/stdc++.h>
using namespace std;

// User function Template for C++
class Solution {
    int findCeil(vector<int>& arr, int x) {
        int n = arr.size();
        int ans = -1;

        int low = 0, high = n-1;

        while(low<=high){
            int mid = low + (high-low)/2;

            if(arr[mid]>=x){
                ans = mid;
                high = mid - 1;
            }
            else{
                low = mid + 1;
            }
        }
        return ans;
    }
    int findFloor(vector<int>& arr, int x) {
        int n = arr.size();
        int ans = -1;

        int low = 0, high = n-1;

        while(low<=high){
            int mid = low + (high-low)/2;

            if(arr[mid]<=x){
                low = mid + 1;
                ans = mid;
            }
            else{
                high = mid - 1;
            }
        }
        return ans;
    }
    public:
    vector<int> findFloorCeil(vector<int> &arr,int x){
        return {findFloor(arr,x),findCeil(arr,x)};
    }
};

int main() {
    return 0;
}