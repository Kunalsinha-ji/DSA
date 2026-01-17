#include <bits/stdc++.h>
using namespace std;

class Solution {
    static bool cmp(pair<double,int> p1, pair<double,int> p2){
        return p1.first>p2.first;
    }
  public:
    double fractionalKnapsack(vector<int>& val, vector<int>& wt, int capacity) {
        // code here
        int n = val.size();
        vector<pair<double,int>> v;

        for(int i=0;i<n;i++){
            double vpw = double(val[i])/double(wt[i]);
            v.push_back({vpw,wt[i]});
        }

        sort(v.begin(),v.end(),cmp);
        int i = 0;
        double res = 0;
        while(i<n && capacity!=0){
            if(capacity>v[i].second){
                capacity -= v[i].second;
                res += (v[i].first * v[i].second);
            }
            else{
                res += (v[i].first * capacity);
                capacity = 0;
            }
            i++;
        }
        return res;
    }
};

int main() {
    return 0;
}