#include <bits/stdc++.h>
using namespace std;

bool findElement(vector<int> &arr,int element){
    for(auto it: arr){
        if(it==element){
            return true;
        }
    }
    return false;
}

int main() {
    return 0;
}