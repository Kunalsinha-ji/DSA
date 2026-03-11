#include <bits/stdc++.h>
using namespace std;

class Solution {
    int solve(vector<int> &weights,int max_wt){
        int days = 1;
        int wt = 0;

        for(auto it: weights){
            if(wt + it>max_wt){
                days++;
                wt = it;
            }
            else    wt += it;
        }
        return days;
    }
public:
    int shipWithinDays(vector<int>& weights, int days) {
        int low = *max_element(weights.begin(),weights.end());
        int high = 0;
        for(auto it: weights){
            high += it;
        }

        int ans = high;

        while(low<=high){
            int mid = low + (high-low)/2;

            int req_days = solve(weights,mid);

            if(req_days<=days){
                ans = mid;
                high = mid - 1;
            }
            else{
                low = mid + 1;
            }
        }
        return ans;
    }
};

int main() {
    return 0;
}