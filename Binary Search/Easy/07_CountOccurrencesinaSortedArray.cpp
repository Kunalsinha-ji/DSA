#include <bits/stdc++.h>
using namespace std;

class Solution {
    int firstOccurence(vector<int> &arr,int x){
        int n = arr.size();
        int ans = -1;

        int low = 0, high = n-1;

        while(low<=high){
            int mid = low + (high-low)/2;

            if(arr[mid]==x){
                ans = mid;
                high = mid - 1;
            }
            else if(arr[mid]>x){
                high = mid - 1;
            }
            else{
                low = mid + 1;
            }
        }
        return ans;
    }
    int lastOccurence(vector<int> &arr,int x){
        int n = arr.size();
        int ans = -1;

        int low = 0, high = n-1;

        while(low<=high){
            int mid = low + (high-low)/2;

            if(arr[mid]==x){
                ans = mid;
                low = mid + 1;
            }
            else if(arr[mid]>x){
                high = mid - 1;
            }
            else{
                low = mid + 1;
            }
        }
        return ans;
    }
  public:
    int countFreq(vector<int>& arr, int target) {
        int first = firstOccurence(arr,target);
        if(first==-1)   return 0;
        int last = lastOccurence(arr,target);
        return last - first + 1;
    }
};


int main() {
    return 0;
}