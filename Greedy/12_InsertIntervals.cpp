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
class Solution {
public:
    vector<vector<int>> insert(vector<vector<int>>& intervals, vector<int>& newInterval) {
        int n = intervals.size();                 // Total number of existing intervals
        vector<vector<int>> ans;                  // Result array to store merged intervals

        int i = 0;                                // Pointer to iterate through intervals
        bool isInserted = 0;                      // Flag to track whether newInterval is inserted or not

        while(i<n){
            if(isInserted==0){                    // If newInterval is not inserted yet
                if(newInterval[0]<=intervals[i][0]){   // Check if newInterval should come before current interval
                    if(ans.size()==0){
                        ans.push_back(newInterval);    // If ans is empty simply push newInterval
                    }
                    else{
                        int end = ans.back()[1];       // Get end of last interval in ans
                        if(end>=newInterval[0]){       // If overlap exists with newInterval
                            ans.back()[1] = max(end,newInterval[1]);  // Merge intervals
                        }
                        else{
                            ans.push_back(newInterval); // Otherwise push newInterval as separate interval
                        }
                    }
                    isInserted = 1;                    // Mark newInterval as inserted
                    continue;  // Using this continue to again visit the interval because here we inserted newInterval
                }
                else{
                    ans.push_back(intervals[i]);   // If we are not inserting newInterval, insert current interval
                }
            }
            else{                                   // If newInterval has already been inserted
                int end = ans.back()[1];             // Get end of last interval in ans
                if(end>=intervals[i][0]){            // Check if current interval overlaps with last interval
                    ans.back()[1] = max(end,intervals[i][1]);  // Merge overlapping intervals
                }
                else{
                    ans.push_back(intervals[i]);     // Otherwise push current interval as it is
                }
            }
            i++;                                     // Move to next interval
        }

        if(isInserted==0){                            // If newInterval was never inserted in the loop
            if(ans.size()==0){
                ans.push_back(newInterval);           // If ans is empty push newInterval
            }
            else{
                int end = ans.back()[1];              // Get end of last interval
                if(end>=newInterval[0]){              // Check if overlap exists
                    ans.back()[1] = max(end,newInterval[1]);  // Merge intervals
                }
                else{
                    ans.push_back(newInterval);       // Otherwise insert newInterval
                }
            }
            isInserted = 1;                           // Mark insertion
        }
        return ans;                                   // Return final merged intervals
    }
};


int main() {
    return 0;
}