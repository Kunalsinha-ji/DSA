#include <bits/stdc++.h>
using namespace std;


bool solve(int i,int sum,vector<int>&arr){
    if(i==0){
        return sum==0;
    }

    bool ntake = solve(i-1,sum,arr);
    if(arr[i-1]<=sum){
        bool take = solve(i-1,sum-arr[i-1],arr);
        ntake = take || ntake;
    }

    return ntake;
}
bool isSubsetPresent(int n, int k, vector<int> &a)
{
    return solve(n,k,a);
}

int main() {
    return 0;
}