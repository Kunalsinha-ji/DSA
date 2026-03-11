#include <bits/stdc++.h>
using namespace std;

class Solution {
    bool isPossible(vector<int> &bloomDay,int day, int bouquets,int setsize){
        int setCount = 0;
        int bouquetCount = 0;
        for(auto it: bloomDay){
            if(it<=day){
                setCount++;
            }
            else{
                setCount = 0;
            }
            if(setCount==setsize){
                bouquetCount++;
                setCount = 0;
            }
        }
        return bouquetCount>=bouquets;
    }
public:
    int minDays(vector<int>& bloomDay, int m, int k) {
        int low = *min_element(bloomDay.begin(),bloomDay.end());
        int high = *max_element(bloomDay.begin(),bloomDay.end());

        int bouquets = m;
        int setsize = k;

        int ans = -1;

        while(low<=high){
            int mid = low + (high-low)/2;

            int possible = isPossible(bloomDay,mid,bouquets,setsize);

            if(possible){
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