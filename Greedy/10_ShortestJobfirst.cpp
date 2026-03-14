#include <bits/stdc++.h>
using namespace std;

// User function Template for C++

//Back-end complete function Template for C++

class Solution {
  public:
    long long solve(vector<int>& bt) {
        int n = bt.size();
        long long avgWtTime = 0;
        sort(bt.begin(),bt.end());

        long long wt = 0;
        for(int i=0;i<n;i++){
            avgWtTime += wt;
            wt += bt[i];
        }

        return avgWtTime/n;
    }
};

int main() {
    return 0;
}