#include <bits/stdc++.h>
using namespace std;

// Brute Force
class Solution {
public:
    vector<vector<int>> merge(vector<vector<int>>& intervals) {
        sort(intervals.begin(),intervals.end());
        int n = intervals.size();

        vector<vector<int>> ans;

        for(int i=0;i<n;i++){
            int start = intervals[i][0];
            int end = intervals[i][1];

            if(ans.size()>0 && intervals[i][1]<=ans.back()[1])  continue;
            for(int j=i+1;j<n;j++){
                if(intervals[j][0]<=end){
                    end = max(end,intervals[j][1]);
                }
                else{
                    break;
                }
            }
            ans.push_back({start,end});
        }
        return ans;
    }
};

// Optimal
class Solution {
public:
    vector<vector<int>> merge(vector<vector<int>>& intervals) {
        sort(intervals.begin(),intervals.end());
        int n = intervals.size();

        vector<vector<int>> ans;

        for(int i=0;i<n;i++){
            if(ans.size()==0){
                ans.push_back(intervals[i]);
            }
            else{
                vector<int> v = ans.back();
                int start = v[0];
                int end = v[1];

                if(end>=intervals[i][0]){
                    end = max(end,intervals[i][1]);
                    ans.back()[1] = end;
                }
                else{
                    ans.push_back(intervals[i]);
                }
            }
        }
        return ans;
    }
};

int main() {
    return 0;
}