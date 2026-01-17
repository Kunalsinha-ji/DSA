#include <bits/stdc++.h>
using namespace std;

class Solution {
  public:
    string findOrder(vector<string> &words) {
        set<char> chars;
        for(auto &w : words)
            for(char c : w)
                chars.insert(c);

        vector<int> adj[26];
        vector<int> indegree(26,0);

        for(int i=0;i<words.size()-1;i++){
            string s1 = words[i];
            string s2 = words[i+1];

            bool check = 0;
            for(int j=0;j<min(s1.size(),s2.size());j++){
                if(s1[j]!=s2[j]){
                    adj[s1[j]-'a'].push_back(s2[j]-'a');
                    indegree[s2[j]-'a']++;
                    check = 1;
                    break;
                }
            }
            if(check==0 && s1.size()>s2.size()){
                return "";
            }
        }

        queue<int> q;

        for(char ch:chars){
            if(indegree[ch-'a']==0){
                q.push(ch-'a');
            }
        }
        string ans = "";

        while(!q.empty()){
            int node = q.front();
            q.pop();
            ans += 'a' + node;

            for(auto it: adj[node]){
                indegree[it]--;
                if(indegree[it]==0){
                    q.push(it);
                }
            }
        }
        return ans.size()==chars.size()? ans: "";
    }
};

int main() {
    return 0;
}