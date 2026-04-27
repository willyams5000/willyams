// ===== DICTIONARY =====
const words = [
"hello","world","want","went","word","school","food","design","developer",
"javascript","html","css","processor","smart","application","text","open","close",
"create","write","wrong","correct","typing","fast","edit","function","code"
];

const freq = {
want: 500,
went: 300,
world: 800,
hello: 900,
code: 700
};

// ===== TRIE =====
class TrieNode{
constructor(){
this.children={};
this.end=false;
}
}

class Trie{
constructor(){
this.root=new TrieNode();
}
insert(word){
let node=this.root;
for(let c of word){
if(!node.children[c]) node.children[c]=new TrieNode();
node=node.children[c];
}
node.end=true;
}
search(word){
let node=this.root;
for(let c of word){
if(!node.children[c]) return false;
node=node.children[c];
}
return node.end;
}
}

const trie=new Trie();
words.forEach(w=>trie.insert(w));

// ===== EDIT DISTANCE =====
const alphabet="abcdefghijklmnopqrstuvwxyz";

function edits1(word){
let results=new Set();

for(let i=0;i<word.length;i++){
results.add(word.slice(0,i)+word.slice(i+1));
}

for(let i=0;i<word.length;i++){
for(let c of alphabet){
results.add(word.slice(0,i)+c+word.slice(i+1));
}
}

for(let i=0;i<=word.length;i++){
for(let c of alphabet){
results.add(word.slice(0,i)+c+word.slice(i));
}
}

return [...results];
}

// ===== SUGGESTION ENGINE =====
function getSuggestion(word){
if(trie.search(word)) return word;

let candidates=edits1(word).filter(w=>trie.search(w));

if(candidates.length===0) return null;

candidates.sort((a,b)=>(freq[b]||1)-(freq[a]||1));

return candidates[0];
}

// ===== UI =====
const editor=document.getElementById("editor");
const box=document.getElementById("suggestBox");

let timer;

editor.addEventListener("input",()=>{
clearTimeout(timer);
timer=setTimeout(process,200);
});

function process(){
let text=editor.innerText;
let arr=text.split(/\s+/);

editor.innerHTML=arr.map(w=>{
if(!w) return "";
let sug=getSuggestion(w.toLowerCase());

if(!sug && w.length>0){
return `<span class="bad-word">${w}</span>`;
}
return w;
}).join(" ");
}

// ===== POPUP =====
editor.addEventListener("mouseup",()=>{
let sel=window.getSelection().toString().trim();
if(!sel) return box.style.display="none";

let sug=getSuggestion(sel.toLowerCase());
if(!sug || sug===sel) return;

let rect=window.getSelection().getRangeAt(0).getBoundingClientRect();

box.style.left=rect.left+"px";
box.style.top=rect.bottom+"px";
box.style.display="block";

box.innerHTML=`<div class="suggestion-item">Replace with <b>${sug}</b></div>`;

box.onclick=()=>{
document.execCommand("insertText",false,sug);
box.style.display="none";
};
});

function clearEditor(){
editor.innerHTML="";
box.style.display="none";
}