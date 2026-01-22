#include <bits/stdc++.h>
using namespace std;

// User function Template for C++

class Solution {
  public:
    void rotate(vector<int> &arr) {
        int n = arr.size();
        if(n==1){
            return;
        }

        int temp = arr[n-1];
        for(int i=n-1;i>=1;i--){
            arr[i] = arr[i-1];
        }
        arr[0] = temp;
    }
};

int main() {
    return 0;
}