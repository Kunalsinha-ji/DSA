#include <bits/stdc++.h>
using namespace std;

class Solution {
    bool solve(int n1,int n2){
        long long int prod = n1 * n1;
        return prod <= n2;
    }
  public:
    int floorSqrt(int n) {
        int low = 1, high = n;
        int ans = 1;
        while(low<=high){
            int mid = low + (high-low)/2;

            int res = solve(mid,n);
            if(res==1){
                low = mid + 1;
                ans = mid;
            }
            else{
                high = mid-1;
            }
        }
        return ans;
    }
};

int main() {
    return 0;
}