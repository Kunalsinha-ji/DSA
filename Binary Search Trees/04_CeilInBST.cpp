#include <bits/stdc++.h>
using namespace std;

class Solution {
  public:
    int findCeil(Node* root, int x) {
        // code here
        int ans = -1;
        Node* curr = root;

        while(curr){
            if(curr->data==x){
                return x;
            }
            else if(curr->data<x){
                curr = curr->right;
            }
            else{
                ans = curr->data;
                curr = curr->left;
            }
        }
        return ans;
    }
};


int main() {
    return 0;
}