#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    bool searchMatrix(vector<vector<int>>& arr, int target) {
        int n = arr.size();
        int m = arr[0].size();

        int low = 0, high = n-1;

        while(low<=high){
            int mid = low + (high-low)/2;

            if(arr[mid][0]==target || arr[mid][m-1]==target){
                return 1;
            }
            if(arr[mid][0]<target && arr[mid][m-1]>target){
                int l = 1, h = m-2;
                while(l<=h){
                    int mm = l + (h-l)/2;

                    if(arr[mid][mm]==target){
                        return 1;
                    }
                    else if(arr[mid][mm]>target){
                        h = mm - 1;
                    }
                    else{
                        l = mm + 1;
                    }
                }
                return 0;
            }
            if(arr[mid][m-1]<target){
                low = mid + 1;
            }
            else{
                high = mid - 1;
            }
        }
        return 0;
    }
};

int main() {
    return 0;
}