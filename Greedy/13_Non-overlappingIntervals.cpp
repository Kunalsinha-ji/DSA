#include <bits/stdc++.h>
using namespace std;

class Solution {
    static bool cmp(vector<int> &v1,vector<int> &v2){
        return v1[1]<v2[1];
    }
public:
    int eraseOverlapIntervals(vector<vector<int>>& intervals) {
        int remove = 0;
        int n = intervals.size();

        sort(intervals.begin(),intervals.end(),cmp);

        int end = intervals[0][1];

        for(int i=1;i<n;i++){
            if(intervals[i][0]<end){
                // This is overlapping remove it
                // once it is removed we don't consider its values at all
                remove++;
            }
            else{
                // Move to next interval and set new end
                end = intervals[i][1];
            }
        }
        return remove;
    }
};

int main() {
    return 0;
}