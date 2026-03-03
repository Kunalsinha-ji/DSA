#include <bits/stdc++.h>
using namespace std;

class Solution {
  public:
    int getSecondLargest(vector<int> &arr) {
        int n = arr.size();
        sort(arr.begin(),arr.end());

        int largest = arr[n-1];
        int secLargest = -1;
        int i = n-2;
        while(i>=0){
            if(arr[i]!=largest){
                secLargest = arr[i];
                break;
            }
            i--;
        }

        return secLargest;
    }
};

class Solution {
  public:
    int getSecondLargest(vector<int> &arr) {
        int n = arr.size();

        int largest = -1,secLargest = -1;

        for(int i=0;i<n;i++){
            if(largest==-1){
                largest = arr[i];
            }
            else if(arr[i]>largest){
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