#include <bits/stdc++.h>
using namespace std;

/*
class Node {
public:
    int data;
    Node* left;
    Node* right;

    Node(int val) {
        data = val;
        left = nullptr;
        right = nullptr;
    }
};
*/

class Solution {
  public:
    vector<int> leftView(Node *root) {
        // code here
        vector<int> ans;
        if(root==NULL)  return ans;
        queue<Node*> q;

        q.push(root);
        q.push(NULL);
        int last = root->data;
        while(!q.empty()){
            Node* node = q.front();
            q.pop();

            if(node==NULL){
                ans.push_back(last);
                if(!q.empty()){
                    q.push(NULL);
                }
                last = -1;
            }
            else{
                if(last==-1)    last = node->data;
                if(node->left){
                    q.push(node->left);
                }
                if(node->right){
                    q.push(node->right);
                }
            }
        }
        return ans;
    }
};

int main() {
    return 0;
}