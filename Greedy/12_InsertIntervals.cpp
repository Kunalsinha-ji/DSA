#include <bits/stdc++.h>
using namespace std;

// Using merge intervals
class Solution {
    vector<vector<int>> merge(vector<vector<int>>& intervals) {
        int n = intervals.size();
        sort(intervals.begin(),intervals.end());

        vector<vector<int>> ans;
        ans.push_back(intervals[0]);

        for(int i=1;i<n;i++){
            int end = ans.back()[1];
            if(end>=intervals[i][0]){
                ans.back()[1] = max(end,intervals[i][1]);
            }
            else{
                ans.push_back(intervals[i]);
            }
        }
        return ans;
    }
public:
    vector<vector<int>> insert(vector<vector<int>>& intervals, vector<int>& newInterval) {
        intervals.push_back(newInterval);
        return merge(intervals);
    }
};

// without using merge intervals


int main() {
    return 0;
}