#include <bits/stdc++.h>
using namespace std;

bool linearSearch(vector<int> &nums,int num){
    for(auto it: nums){
        if(it==num) return 1;
    }
    return 0;
}

int main() {
    return 0;
}