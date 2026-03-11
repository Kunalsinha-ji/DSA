#include <bits/stdc++.h>
using namespace std;

class Solution {
    bool solve(vector<int> &stalls,int dist,int cows){
        int cow = 1; // first cow kept at first index
        int lastCowInd = 0;

        for(int i=1;i<stalls.size();i++){
            if(stalls[i]-stalls[lastCowInd]>=dist){
                cow++;
                lastCowInd = i;
            }
        }
        return cow>=cows;
    }
  public:
    int aggressiveCows(vector<int> &stalls, int k) {
        sort(stalls.begin(),stalls.end());
        int n = stalls.size();
        int low = 1; // min dist that can be kept
        int high = stalls[n-1] - stalls[0]; // max dist that can be b/w 2 cows

        int ans = low;

        while(low<=high){
            int mid = low + (high-low)/2;

            bool canFit = solve(stalls,mid,k);

            if(canFit){
                ans = mid;
                // try increasing dist a bit
                low = mid + 1;
            }
            else{
                // Decrease distance
                high = mid - 1;
            }
        }
        return ans;
    }
};

int main() {
    return 0;
}