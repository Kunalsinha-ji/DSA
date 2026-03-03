#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    vector<int> findMissingAndRepeatedValues(vector<vector<int>>& grid) {
        int n = grid.size();
        int m = grid[0].size();

        int numbers = n*m;
        long long int sum1 = (numbers*(numbers+1))/2;
        long long int sum2 = 0;
        unordered_map<int,int> mp;
        int repeated = -1;

        for(int i=0;i<n;i++){
            for(int j=0;j<m;j++){
                sum2 += grid[i][j];
                mp[grid[i][j]]++;
                if(mp[grid[i][j]]>1){
                    repeated = grid[i][j];
                }
            }
        }

        int diff1 = int(sum1 - sum2);  // missing - repeated
        int missing = diff1+repeated;
        return {repeated,missing};
    }
};

// 2nd type
class Solution {
  public:
    vector<int> findTwoElement(vector<int>& arr) {
        int n = arr.size();
        unordered_map<int,int> mp;
        int repeated = -1;

        long long int orgSum = (n * (n+1))/2;
        long long int currSum = 0;

        for(int i=0;i<n;i++){
            currSum += arr[i];
            mp[arr[i]]++;
            if(mp[arr[i]]>1){
                repeated = arr[i];
            }
        }

        int diff = int(orgSum-currSum);   // missing - repeated
        int missing = diff + repeated;

        return {repeated,missing};
    }
};

int main() {
    return 0;
}