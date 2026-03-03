#include <bits/stdc++.h>
using namespace std;

vector<int> printMaxSubarray(vector<int> &arr){
    int n = arr.size();
    int sum = 0, maxSum = INT_MIN;
    vector<int> ans;

    for(int i=0;i<n;i++){
        sum += arr[i];
        arr.push_back(arr[i]);
        if(sum>maxSum){
            maxSum = sum;
        }
        if(sum<0){
            sum = 0;
            ans.clear();
        }
    }
    return ans;
}

int main() {
    return 0;
}