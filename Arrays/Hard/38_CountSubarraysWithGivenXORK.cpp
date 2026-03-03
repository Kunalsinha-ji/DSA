#include <bits/stdc++.h>
using namespace std;

// Brute force
class Solution {
  public:
    long subarrayXor(vector<int> &arr, int k) {
        int n = arr.size();
        long cnt = 0;

        for(int i=0;i<n;i++){
            for(int j=i;j<n;j++){
                int xr = 0;
                for(int l=i;l<=j;l++){
                    xr ^= arr[l];
                }
                if(xr==k){
                    cnt++;
                }
            }
        }
        return cnt;
    }
};

// Better
class Solution {
  public:
    long subarrayXor(vector<int> &arr, int k) {
        int n = arr.size();
        long cnt = 0;

        for(int i = 0; i < n; i++){
            int xr = 0;
            for(int j = i; j < n; j++){
                xr ^= arr[j];
                if(xr == k){
                    cnt++;
                }
            }
        }
        return cnt;
    }
};

// Optimal
class Solution {
  public:
    long subarrayXor(vector<int> &arr, int k) {
        int n = arr.size();
        long cnt = 0;
        int xr = 0;
        unordered_map<int,int> mp;
        mp[xr] = 1; // this tells xor of 0 is once occuring if no elements taken

        for(int i=0;i<n;i++){
            xr ^= arr[i];

            // k ^ left = xr --> left = xr ^ k
            int left = xr ^ k;
            cnt += mp[left];
            mp[xr]++;
        }
        return cnt;
    }
};

int main() {
    return 0;
}