#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    vector<vector<string>> findLadders(string beginWord, string endWord, vector<string>& wordList) {
        vector<vector<string>> ans;
        unordered_set<string> st(wordList.begin(),wordList.end());

        vector<string> vis;
        queue<vector<string>> q;
        q.push({beginWord});
        vis.push_back(beginWord);
        int len = 0;

        while(!q.empty()){
            vector<string> v = q.front();
            q.pop();

            string word = v.back();
            if(word==endWord){
                if(ans.size()==0){
                    ans.push_back(v);
                }
                else{
                    if(v.size()==ans[0].size()){
                        ans.push_back(v);
                    }
                }
            }

            if(v.size()>len){
                for(auto it: vis){
                    st.erase(it);
                }
                len++;
            }

            for(int i=0;i<word.size();i++){
                char org = word[i];
                for(char ch='a';ch<='z';ch++){
                    word[i] = ch;
                    if(st.find(word)!=st.end()){
                        v.push_back(word);
                        q.push(v);
                        v.pop_back();
                        vis.push_back(word);
                    }
                }
                word[i] = org;
            }
        }
        return ans;
    }
};

int main() {
    return 0;
}