#include <bits/stdc++.h>
using namespace std;

class Solution {
  public:
    int getSecondLargest(vector<int> &arr) {
        int largest = -1,secLargest = -1;

        for(int i=0;i<arr.size();i++){
            if(arr[i]>largest){
                secLargest = largest;
                largest = arr[i];
            }
            else if(arr[i]<largest && arr[i]>secLargest){
                secLargest = arr[i];
            }
        }

        return secLargest;
    }
};

int main() {
    return 0;
}