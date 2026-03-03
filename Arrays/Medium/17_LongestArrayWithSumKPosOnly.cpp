#include <bits/stdc++.h>
using namespace std;

// Brute force
int solve(vector<int> &arr,int k){
    int n = arr.size();
    int maxLen = -1;

    for(int i=0;i<n;i++){
        int sum = 0;
        for(int j=i;j<n;j++){
            sum += arr[j];
            if(sum==k){
                int len = j-i+1;
                maxLen = max(maxLen,len);
            }
            if(sum>k){
                break;
            }
        }
    }
    return maxLen;
}

// Optimal
int solveOptimal(vector<int> &arr,int k){
    int n = arr.size();
    int maxLen = -1;
    unordered_map<int,int> mp;
    int sum = 0;
    mp[sum] = -1;

    for(int i=0;i<n;i++){
        sum += arr[i];

        // sum - left = k
        int left = sum-k;

        if(mp.find(left)!=mp.end()){
            int len = i - mp[left];
            maxLen = max(maxLen,len);
        }
        if(mp.find(sum)==mp.end()){
            mp[sum] = i;
        }
    }
    return maxLen;
}

int main() {
    return 0;
}