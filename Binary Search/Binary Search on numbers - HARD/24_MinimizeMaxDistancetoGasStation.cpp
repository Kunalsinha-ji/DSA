#include <bits/stdc++.h>
using namespace std;

class Solution {
    int solve(vector<int> &stations, double dist){
        int count = 0;

        for(int i = 0; i < stations.size() - 1; i++){
            double gap = stations[i+1] - stations[i];
            int need = gap / dist;

            if(gap == need * dist) need--;

            count += need;
        }
        return count;
    }

public:
    double minMaxDist(vector<int> &stations, int K) {
        double low = 0;
        double high = 0;

        for(int i = 0; i < stations.size() - 1; i++){
            high = max(high, (double)(stations[i+1] - stations[i]));
        }

        while(high - low > 1e-6){
            double mid = (low + high) / 2.0;

            if(solve(stations, mid) > K)
                low = mid;
            else
                high = mid;
        }

        return high;
    }
};


int main() {
    return 0;
}