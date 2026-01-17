#include <bits/stdc++.h>
using namespace std;

class Solution {
  public:
    int floor(Node* root, int x) {
        // code here
        int ans = -1;

        while(root){
            if(root->data==x){
                return x;
            }

            if(root->data<x){
                ans = root->data;
                root = root->right;
            }
            else{
                root = root->left;
            }
        }
        return ans;
    }
};

int main() {
    return 0;
}