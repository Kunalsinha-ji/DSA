#include <bits/stdc++.h>
using namespace std;

// Brute force
class Solution {
  public:
    int inversionCount(vector<int> &arr) {
        int n = arr.size();

        int count = 0;
        for(int i=0;i<n;i++){
            for(int j=i+1;j<n;j++){
                if(arr[j]<arr[i]){
                    count++;
                }
            }
        }
        return count;
    }
};


// Optimal -> Using merge sort
class Solution {
    int merge(vector<int> &arr,int l,int mid,int h){
        vector<int> temp;
        int count = 0;
        int i = l,j=mid+1;

        while(i<=mid && j<=h){
            if(arr[i]<=arr[j]){
                temp.push_back(arr[i]);
                i++;
            }
            else{
                count += (mid-i+1);
                temp.push_back(arr[j]);
                j++;
            }
        }

        while(i<=mid){
            temp.push_back(arr[i]);
            i++;
        }
        while(j<=h){
            temp.push_back(arr[j]);
            j++;
        }
        for(int k=0;k<temp.size();k++){
            arr[l++] = temp[k];
        }
        return count;
    }
    int mergeSort(vector<int> &arr,int l,int h){
        if(l>=h){
            return 0;
        }

        int count = 0;
        int mid = (l+h)/2;
        count += mergeSort(arr,l,mid);
        count += mergeSort(arr,mid+1,h);
        count += merge(arr,l,mid,h);
        return count;
    }
  public:
    int inversionCount(vector<int> &arr) {
        int n = arr.size();
        return mergeSort(arr,0,n-1);
    }
};

int main() {
    return 0;
}