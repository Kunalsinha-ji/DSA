#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    bool check(vector<int>& arr) {
        int n = arr.size();
        if(n==1){
            return 1;
        }

        int ind = 1;
        while(ind<n){
            if(arr[ind]<arr[ind-1]){
                break;
            }
            ind++;
        }

        if(ind==n)  return 1;
        for(int i=0;i<n-1;i++){
            if(arr[(i+ind)%n]>arr[(i+1+ind)%n]){
                return 0;
            }
        }
        return 1;
    }
};

int main() {
    return 0;
}