#include <bits/stdc++.h>
using namespace std;

class Solution {
    int solve(vector<int> &arr,int canPaintMax){
        int n = arr.size();

        int painter = 1;
        int sumPaint = 0;

        for(int it : arr){
            if(it+sumPaint>canPaintMax){
                painter++;
                sumPaint = it;
            }
            else{
                sumPaint += it;
            }
        }
        return painter;
    }
  public:
    int minTime(vector<int>& arr, int k) {
        int n = arr.size();
        int low = *max_element(arr.begin(),arr.end());
        // atleast a painter can paint a board of max length
        int high = 0;

        for(auto it: arr){
            high += it;
        }
        // A painter can paint all

        while(low<=high){
            int mid = low + (high-low)/2;

            int paintersReq = solve(arr,mid);

            if(paintersReq>k){
                low = mid + 1;
            }
            else{
                high = mid - 1;
            }
        }
        return low;
    }
};

int main() {
    return 0;
}