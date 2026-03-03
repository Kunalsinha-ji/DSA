#include <bits/stdc++.h>
using namespace std;

// Sort and find n log n
class Solution {
  public:
    int largest(vector<int> &arr) {
        int n = arr.size();
        sort(arr.begin(),arr.end());
        return arr[n-1];
    }
};

// O(n)
class Solution {
  public:
    int largest(vector<int> &arr) {
        int n = arr.size();
        int largest = arr[0];

        for(int i=1;i<n;i++){
            largest = max(largest,arr[i]);
        }
        return largest;
    }
};


int main() {
    return 0;
}