// {"name": "Markov Chain", "tags": ["markov", "generative", "algorithm", "utility"], "tempo": 120, "description": "Simple Markov chain implementation for pattern generation", "author": null, "version": "1.0.0", "date": "2025-12-26"}
let markovstates = {};
                   
let markovtables = {
  'drums':
  [[  0,  .2,  .8],
   [ .3,   0,  .7],
   [ .9,  .1,   0]]

, 'chords':  
  [[  .2,  .2,  .4,  .2],  
   [ .5,   .3,  .2,  .1],
   [  0,   .2,   .7,  .1],
   [ .7,  .1,   .1,  .1]] 
 }

const markov = register('markov', (id, pat) => pat.withHap((hap)=> {   

     if(markovstates[id]===undefined) markovstates[id]=[0];
     const mystate = markovstates[id];
     const mytable = markovtables[id];
  
     const p = hap.whole.begin.n;
     while(mystate.length<=p)
       {
         const prev = mystate[mystate.length-1];
         const t = mytable[prev];
         let next = prev;
         for(let i=0,j=t[i];i<t.length;i++,j+=t[i]) if(hap.value<j) { next = i; break; }
         mystate.push(next);
       }
     return hap.withValue((v)=>mystate[p]);
}))