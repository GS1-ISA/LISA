function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');}
function el(id){ return document.getElementById(id); }
async function api(path, method='GET', body){ 
  const res = await fetch(path, {method, headers:{'Content-Type':'application/json'}, body: body?JSON.stringify(body):undefined});
  if(!res.ok) throw new Error(await res.text()); return res.json();
}
function addFeedbackUI(container, ctx){
  const div=document.createElement('div'); div.className='feedback';
  div.innerHTML=`<span>Feedback:</span><button>👍</button><button>👎</button><button>Comment</button>`;
  const [up,down,comment]=div.querySelectorAll('button');
  up.onclick=()=>api('/feedback','POST',{context:ctx,type:'thumbs',value:'up'}).catch(()=>{});
  down.onclick=()=>api('/feedback','POST',{context:ctx,type:'thumbs',value:'down'}).catch(()=>{});
  comment.onclick=()=>{const t=prompt('Your comment'); if(t){ api('/feedback','POST',{context:ctx,type:'comment',text:t}); }};
  container.appendChild(div);
}
document.addEventListener('DOMContentLoaded', ()=>{
});