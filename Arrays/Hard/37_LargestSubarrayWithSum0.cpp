#include <bits/stdc++.h>
using namespace std;

// Brute force
class Solution {
  public:
    int maxLength(vector<int>& arr) {
        int n = arr.size();
        int maxLen = 0;
        for(int i=0;i<n;i++){
            int sum = 0;
            for(int j=i;j<n;j++){
                sum += arr[j];
                if(sum==0){
                    int len = j-i+1;
                    maxLen = max(maxLen,len);
                }
            }
        }
        return maxLen;
    }
};

// Optimal
class Solution {
  public:
    int maxLength(vector<int>& arr) {
        int n = arr.size();
        int maxLen = 0;
        unordered_map<int,int> mp;
        int sum = 0;
        mp[sum] = -1;

        for(int i=0;i<n;i++){
            sum += arr[i];
            // sum - k = 0  --> k = sum : to find if k exists in map and at which index
            if(mp.find(sum)!=mp.end()){
                int len = i - mp[sum];
                maxLen = max(maxLen,len);
            }
            else{
                mp[sum] = i;
            }
        }
        return maxLen;
    }
};

int main() {
    return 0;
}