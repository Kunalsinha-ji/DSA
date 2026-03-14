#include <bits/stdc++.h>
using namespace std;

class Solution {
  public:
    double fractionalKnapsack(vector<int>& val, vector<int>& wt, int capacity) {
        vector<pair<double,int>> arr;

        for(int i=0;i<val.size();i++){
            int v = val[i];
            int w = wt[i];

            double costPerWt = double(v)/double(w);

            arr.push_back({costPerWt,w});
        }

        sort(arr.rbegin(),arr.rend());

        double ans = 0;

        for(auto it : arr){
            int wgt = it.second;
            double vv = it.first;

            if(capacity>=wgt){
                ans += double(vv * wgt);
                capacity -= wgt;
            }
            else{
                ans += double(vv * capacity);
                capacity = 0;
            }
        }
        return ans;
    }
};


int main() {
    return 0;
}