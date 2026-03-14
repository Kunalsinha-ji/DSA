#include <bits/stdc++.h>
using namespace std;

class Solution {
    static bool cmp(vector<int> &v1,vector<int> &v2){
        return v1[1]<v2[1];
    }
public:
    int eraseOverlapIntervals(vector<vector<int>>& intervals) {
        int n = intervals.size();
        sort(intervals.begin(),intervals.end(),cmp);

        int end = intervals[0][1];
        int remove = 0;
        for(int i=1;i<n;i++){
            if(end>intervals[i][0]){
                // This is overlapping hence remove it
                // if we remove it we don't even consider it
                remove++;
            }
            else{
                end = intervals[i][1];
            }
        }
        return remove;
    }
};

int main() {
    return 0;
}