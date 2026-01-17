#include <bits/stdc++.h>
using namespace std;

pair<int,int> MinMaxInBst(TreeNode* root){
    if(root==NULL){
        return {-1,-1};
    }

    TreeNode* curr=root;
    while(curr->left!=NULL){
        curr=curr->left;
    }
    int mini=curr->val;

    curr=root;
    while(curr->right!=NULL){
        curr=curr->right;
    }
    int maxi=curr->val;

    return {mini,maxi};
}
int main() {
    return 0;
}