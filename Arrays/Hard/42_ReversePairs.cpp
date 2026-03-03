#include <bits/stdc++.h>
using namespace std;

// Brute force
class Solution {
public:
    int reversePairs(vector<int>& nums) {
        int n = nums.size();
        int count = 0;
        for(int i=0;i<n;i++){
            for(int j=i+1;j<n;j++){
                if(nums[i]>2*nums[j]){
                    count++;
                }
            }
        }
        return count;
    }
};

// Optimal approach
class Solution {
    void merge(vector<int> &arr,int l,int mid,int h){
        vector<int> temp;
        int i = l,j = mid+1;
        while(i<=mid && j<=h){
            if(arr[i]<=arr[j]){
                temp.push_back(arr[i]);
                i++;
            }
            else{
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
    }
    int counter(vector<int> &arr,int l,int mid,int h){
        int count = 0;
        int j = mid+1;
        for(int i=l;i<=mid;i++){
            while(j<=h && arr[i]>2*arr[j]){
                j++;
            }
            count += (j-mid-1);
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
        count += counter(arr,l,mid,h);
        merge(arr,l,mid,h);
        return count;
    }
public:
    int reversePairs(vector<int>& nums) {
        int n = nums.size();
        return mergeSort(nums,0,n-1);
    }
};

int main() {
    return 0;
}