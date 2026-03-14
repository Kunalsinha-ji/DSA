#include <bits/stdc++.h>
using namespace std;

class Solution {
  public:
    vector<int> jobSequencing(vector<int> &deadline, vector<int> &profit) {
        int maxDays = 0;
        vector<pair<int,int>> arr;
        for(int i=0;i<deadline.size();i++){
            maxDays = max(maxDays,deadline[i]);
            arr.push_back({profit[i],deadline[i]});
        }

        sort(arr.rbegin(),arr.rend());
        vector<int> freeDays(maxDays+1,-1);

        int job = 0;
        int prof = 0;

        for(auto it: arr){
            int p = it.first;
            int dl = it.second;

            while(dl>0){
                if(freeDays[dl]==-1){
                    freeDays[dl] = 1;
                    prof += p;
                    job++;
                    break;
                }
                dl--;
            }
        }
        return {job,prof};
    }
};

int main() {
    return 0;
}