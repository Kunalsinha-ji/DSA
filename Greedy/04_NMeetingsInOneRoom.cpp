#include <bits/stdc++.h>
using namespace std;

class Solution {
    static bool cmp(pair<int,int> &p1, pair<int,int> &p2){
        return p1.second < p2.second;
    }
  public:
    // Function to find the maximum number of meetings that can
    // be performed in a meeting room.
    int maxMeetings(vector<int>& start, vector<int>& end) {
        int ans = 1;

        vector<pair<int,int>> arr;

        for(int i=0;i<start.size();i++){
            arr.push_back({start[i],end[i]});
        }

        sort(arr.begin(),arr.end(),cmp);

        int ending = arr[0].second;

        for(int i=1;i<arr.size();i++){
            if(arr[i].first>ending){
                ending = arr[i].second;
                ans++;
            }
        }
        return ans;
    }
};

int main() {
    return 0;
}