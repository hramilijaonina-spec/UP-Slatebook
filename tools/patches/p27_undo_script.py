# Annuler / rétablir partout : scénario (frappe, scènes ajoutées, fusion, renumérotation), nettoyage de texte, lieux de tournage,
# pages par jour ; réglages du projet annulés champ par champ (sans réécrire tout le projet).
import re, sys
p = sys.argv[1]; t = open(p, encoding="utf-8").read()
def R(a, b, n=1):
    global t
    c = t.count(a)
    assert c == n, (a[:90], c)
    t = t.replace(a, b)

# --- moteur : commentaires suivis, réglages du projet champ par champ, étapes sans changement ignorées, frappe regroupée ---
R('''col==="locations"?S.locations:null;if(arr)v=arr.find(x=>x.id===id)||null;}''',
  '''col==="locations"?S.locations:col==="comments"?S.comments:null;if(arr)v=arr.find(x=>x.id===id)||null;}''')
R('''function hRec(path,before,after,label,key){
  if(H.applying)return;H.shadow.set(path,hClone(after));
  if(H.grp){H.grp.ops.push({path,before,after:hClone(after)});return;}''', '''/* deux états identiques (hors date et auteur de la modification) : rien à annuler */
const hSame=(a,b)=>{const c=v=>{if(!v)return v;const{updatedAt,updatedBy,...r}=v;return JSON.stringify(snapNorm(r))||"";};return c(a)===c(b);};
const isProjPath=path=>/^projects\\/[^/]+$/.test(path);
function hRec(path,before,after,label,key,patch){
  if(H.applying)return;if(!patch)H.shadow.set(path,hClone(after));
  if(hSame(before,after))return;
  if(H.grp){H.grp.ops.push({path,before,after:hClone(after),patch:!!patch});return;}''')
R('''  else{H.undo.push({label:label||"Modification",key:key||null,at:Date.now(),ops:[{path,before,after:hClone(after)}]});if(H.undo.length>80)H.undo.shift();}''',
  '''  else{H.undo.push({label:label||"Modification",key:key||null,at:Date.now(),ops:[{path,before,after:hClone(after),patch:!!patch}]});if(H.undo.length>80)H.undo.shift();}''')
R('''  async update(d,o={}){const before=o.before!==undefined?o.before:hCur(path);await ref.update(d);hRec(path,before,before?{...before,...d}:d,o.label,o.key);},''',
  '''  async update(d,o={}){
    /* projet : on ne garde que les champs changés, pour ne pas réécrire tout le projet (membres, rôles…) en annulant */
    if(isProjPath(path)){const cur=hCur(path)||{};const before={};for(const k of Object.keys(d))before[k]=cur[k]===undefined?null:cur[k];await ref.update(d);hRec(path,before,{...d},o.label,o.key,true);return;}
    const before=o.before!==undefined?o.before:hCur(path);await ref.update(d);hRec(path,before,before?{...before,...d}:d,o.label,o.key);},''')
R('''async function hGroup(label,fn){
  if(H.grp)return fn();
  H.grp={label,ops:[],at:Date.now()};
  try{return await fn();}
  finally{const g=H.grp;H.grp=null;if(g.ops.length){H.undo.push(g);if(H.undo.length>80)H.undo.shift();H.redo=[];}hButtons();}
}
async function hApply(path,val){const r=S.db.doc(path);if(val==null){try{await r.delete();}catch{}}else await r.set(val);H.shadow.set(path,hClone(val));}''',
  '''async function hGroup(label,fn,key){
  if(H.grp)return fn();
  H.grp={label,key:key||null,ops:[],at:Date.now(),t0:Date.now()};
  try{return await fn();}
  finally{const g=H.grp;H.grp=null;
    if(g.ops.length){const last=H.undo[H.undo.length-1];const now=Date.now();
      /* frappe continue dans la même scène : une seule étape (jusqu'à 6 s de pause, 20 s au plus) */
      if(key&&last&&last.key===key&&now-last.at<6000&&now-(last.t0||last.at)<20000&&g.ops.length===1&&last.ops.length===1&&last.ops[0].path===g.ops[0].path&&g.ops[0].before){last.ops[0].after=g.ops[0].after;last.at=now;}
      else{H.undo.push(g);if(H.undo.length>80)H.undo.shift();}
      H.redo=[];}
    hButtons();}
}
async function hApply(path,val,patch){const r=S.db.doc(path);
  if(patch){await r.update(val||{});return;}
  if(val==null){try{await r.delete();}catch{}}else await r.set(val);H.shadow.set(path,hClone(val));}''')
R('''  H.busy=true;H.applying=true;hButtons();
  try{const ops=dir<0?[...st.ops].reverse():st.ops;for(const o of ops)await hApply(o.path,dir<0?o.before:o.after);''',
  '''  H.busy=true;H.applying=true;hButtons();const edf=edHistoryStart();
  try{const ops=dir<0?[...st.ops].reverse():st.ops;for(const o of ops)await hApply(o.path,dir<0?o.before:o.after,o.patch);''')
R('''  finally{H.applying=false;H.busy=false;ED.sigs.clear();render();hButtons();}
}''', '''  finally{H.applying=false;H.busy=false;ED.sigs.clear();render();hButtons();edHistoryEnd(edf);}
}
/* scénario : on quitte le bloc en cours pour que le texte annulé s'affiche, puis on remet le curseur au même endroit */
function edHistoryStart(){
  const page=$("#edpage");const a=document.activeElement;if(!page||!a||!page.contains(a))return null;
  const el=a.closest(".sb"),sec=a.closest(".ed-scene");let f=null;
  if(el&&sec)f={sid:sec.dataset.sid,idx:[...sec.querySelectorAll(".sb")].indexOf(el),caret:caretOffset(el)};
  ED.hist=true;a.blur();return f;
}
function edHistoryEnd(f){
  setTimeout(()=>{ED.hist=false;ED.sigs.clear();if(f&&scene(f.sid))ED.focus=f;render();},250);
}''')
# raccourcis : aussi dans l'onglet Scénario, y compris pendant la frappe
R('''  if(!["dec","scenes","plan"].includes(S.tab)||S.home||!S.pid||!S.canWrite||document.querySelector(".scrim"))return;
  const mod=e.metaKey||e.ctrlKey;if(!mod)return;const k=e.key.toLowerCase();
  if(k!=="z"&&k!=="y")return;
  const tg=e.target;if(tg.closest&&tg.closest("input,textarea,select,[contenteditable]"))return;''',
  '''  if(!["script","dec","scenes","plan"].includes(S.tab)||S.home||!S.pid||!S.canWrite||document.querySelector(".scrim"))return;
  const mod=e.metaKey||e.ctrlKey;if(!mod||e.altKey)return;const k=e.key.toLowerCase();
  if(k!=="z"&&k!=="y")return;
  const tg=e.target;if(tg.closest&&tg.closest("input,textarea,select"))return;
  if(tg.closest&&tg.closest("[contenteditable]")&&!tg.closest("#edpage"))return;''')

# --- scénario : chaque enregistrement devient une étape annulable ---
R('''async function commitScene(sid){
  clearTimeout(ED.timers.get(sid));''', '''async function commitScene(sid){
  if(H.applying||ED.hist){return;}
  const s=scene(sid);return hGroup("Scénario · scène "+(s?.num||""),()=>commitSceneRaw(sid),"ed:"+sid);
}
async function commitSceneRaw(sid){
  clearTimeout(ED.timers.get(sid));''')
R('''    await S.db.doc(base()+"/scenes/"+sid).update(patch);
    if(groups.length){''', '''    await trk(base()+"/scenes/"+sid).update(patch);
    if(groups.length){''')
R('''        await ref.set({...headingFields(g.h,s),num:lastNum,order:lo,blocks:gb,body:bodyFromBlocks(gb),status:"todo",synopsis:"",
          eighths:Math.max(1,Math.round(sceneLines({blocks:gb})/LINES_PER_PAGE*8)),createdAt:Date.now(),createdBy:S.me?.id||null});''',
  '''        await trk(base()+"/scenes/"+ref.id).set({...headingFields(g.h,s),num:lastNum,order:lo,blocks:gb,body:bodyFromBlocks(gb),status:"todo",synopsis:"",
          eighths:Math.max(1,Math.round(sceneLines({blocks:gb})/LINES_PER_PAGE*8)),createdAt:Date.now(),createdBy:S.me?.id||null},{before:null});''')
R('''  await S.db.doc(base()+"/scenes/"+into.id).update({blocks,body:bodyFromBlocks(blocks),eighths:Math.max(1,Math.round(sceneLines({blocks})/LINES_PER_PAGE*8)),updatedAt:Date.now()});
  await chunked(S.elements.filter(e=>e.sceneId===s.id),5,e=>S.db.doc(base()+"/elements/"+e.id).update({sceneId:into.id}));
  await chunked(S.comments.filter(c=>c.sceneId===s.id),5,c=>S.db.doc(base()+"/comments/"+c.id).update({sceneId:into.id}));
  await chunked(S.shots.filter(x=>x.sceneId===s.id),5,x=>S.db.doc(base()+"/shots/"+x.id).update({sceneId:into.id,pos:(x.pos||0)+1e7}));
  await S.db.doc(base()+"/scenes/"+s.id).delete();''',
  '''  await trk(base()+"/scenes/"+into.id).update({blocks,body:bodyFromBlocks(blocks),eighths:Math.max(1,Math.round(sceneLines({blocks})/LINES_PER_PAGE*8)),updatedAt:Date.now()});
  await chunked(S.elements.filter(e=>e.sceneId===s.id),5,e=>trk(base()+"/elements/"+e.id).update({sceneId:into.id}));
  await chunked(S.comments.filter(c=>c.sceneId===s.id),5,c=>trk(base()+"/comments/"+c.id).update({sceneId:into.id}));
  await chunked(S.shots.filter(x=>x.sceneId===s.id),5,x=>trk(base()+"/shots/"+x.id).update({sceneId:into.id,pos:(x.pos||0)+1e7}));
  await trk(base()+"/scenes/"+s.id).delete();''')
R('''try{await chunked(S.scenes.map((s,i)=>({s,n:String(i+1)})).filter(x=>x.s.num!==x.n),5,x=>S.db.doc(base()+"/scenes/"+x.s.id).update({num:x.n}));toast("Scènes renumérotées.");}''',
  '''try{await hGroup("Renuméroter les scènes",()=>chunked(S.scenes.map((s,i)=>({s,n:String(i+1)})).filter(x=>x.s.num!==x.n),5,x=>trk(base()+"/scenes/"+x.s.id).update({num:x.n})));toast("Scènes renumérotées.");}''')
# boutons ↶ ↷ dans la barre du scénario
R('''        ${S.canWrite?`<button class="btn small" id="ed-renum">Renuméroter</button>`:""}''',
  '''        ${S.canWrite?`<button class="btn ghost small icbtn h-undo" type="button" aria-label="Annuler"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 14 4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 0 11H11"/></svg></button><button class="btn ghost small icbtn h-redo" type="button" aria-label="Rétablir"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m15 14 5-5-5-5"/><path d="M20 9H9.5a5.5 5.5 0 0 0 0 11H13"/></svg></button>`:""}
        ${S.canWrite?`<button class="btn small" id="ed-renum">Renuméroter</button>`:""}''')
R('''    bindEditor(root);}''', '''    bindEditor(root);hButtons();}''')
R('''.ed-bar{''', '''.ed-bar .h-undo,.ed-bar .h-redo{min-width:32px;padding-inline:6px}
.ed-bar{''')

# --- autres actions encore sans annulation ---
R('''    try{await chunked(r.scs,5,sc=>S.db.doc(base()+"/scenes/"+sc.id).update({body:stripPhrases(sc.body,[r.ph]),updatedAt:Date.now()}));
      await chunked(r.els,5,e=>S.db.doc(base()+"/elements/"+e.id).delete());''',
  '''    try{await hGroup("Retirer « "+r.ph.slice(0,40)+" »",async()=>{await chunked(r.scs,5,sc=>trk(base()+"/scenes/"+sc.id).update({body:stripPhrases(sc.body,[r.ph]),updatedAt:Date.now()}));
      await chunked(r.els,5,e=>trk(base()+"/elements/"+e.id).delete());});''')
R('''      try{await S.db.collection(base()+"/locations").add({name:n.slice(0,120),address:a.slice(0,240),decors:[],createdAt:Date.now()});}catch(e){writeErr(e);}};''',
  '''      try{await trk(base()+"/locations/"+uid()).set({name:n.slice(0,120),address:a.slice(0,240),decors:[],createdAt:Date.now()},{before:null,label:"Lieu « "+n.slice(0,40)+" » ajouté"});}catch(e){writeErr(e);}};''')
R('''    box.querySelectorAll(".lx-n").forEach(i=>i.onchange=()=>{const v=i.value.trim();if(v)S.db.doc(base()+"/locations/"+i.dataset.lid).update({name:v}).catch(writeErr);});
    box.querySelectorAll(".lx-a").forEach(i=>i.onchange=()=>S.db.doc(base()+"/locations/"+i.dataset.lid).update({address:i.value.trim()}).catch(writeErr));
    box.querySelectorAll(".lx-del").forEach(b=>b.onclick=()=>S.db.doc(base()+"/locations/"+b.dataset.lid).delete().catch(writeErr));''',
  '''    box.querySelectorAll(".lx-n").forEach(i=>i.onchange=()=>{const v=i.value.trim();if(v)trk(base()+"/locations/"+i.dataset.lid).update({name:v},{label:"Nom du lieu"}).catch(writeErr);});
    box.querySelectorAll(".lx-a").forEach(i=>i.onchange=()=>trk(base()+"/locations/"+i.dataset.lid).update({address:i.value.trim()},{label:"Adresse du lieu"}).catch(writeErr));
    box.querySelectorAll(".lx-del").forEach(b=>b.onclick=()=>trk(base()+"/locations/"+b.dataset.lid).delete({label:"Lieu supprimé"}).catch(writeErr));''')
R('''  try{
    for(const l of S.locations){if((l.decors||[]).includes(key)&&l.id!==lid)await S.db.doc(base()+"/locations/"+l.id).update({decors:(l.decors||[]).filter(k=>k!==key)});}
    const t=S.locations.find(l=>l.id===lid);if(t&&!(t.decors||[]).includes(key))await S.db.doc(base()+"/locations/"+t.id).update({decors:[...(t.decors||[]),key]});
  }catch(e){writeErr(e);}''', '''  try{await hGroup("Lieu de tournage d'un décor",async()=>{
    for(const l of S.locations){if((l.decors||[]).includes(key)&&l.id!==lid)await trk(base()+"/locations/"+l.id).update({decors:(l.decors||[]).filter(k=>k!==key)});}
    const t=S.locations.find(l=>l.id===lid);if(t&&!(t.decors||[]).includes(key))await trk(base()+"/locations/"+t.id).update({decors:[...(t.decors||[]),key]});
  });}catch(e){writeErr(e);}''')
R('''if(v===(Number(P()?.pagesPerDay)||4))return;S.db.doc("projects/"+S.pid).update({pagesPerDay:v}).catch(writeErr);};''',
  '''if(v===(Number(P()?.pagesPerDay)||4))return;trk("projects/"+S.pid).update({pagesPerDay:v},{label:"Pages par jour"}).catch(writeErr);};''')
R('''  const t=$("#target");if(t)t.onchange=()=>{const v=Math.max(0.5,Math.min(20,Number(t.value)||4));S.db.doc("projects/"+S.pid).update({pagesPerDay:v}).catch(writeErr);};''',
  '''  const t=$("#target");if(t)t.onchange=()=>{const v=Math.max(0.5,Math.min(20,Number(t.value)||4));trk("projects/"+S.pid).update({pagesPerDay:v},{label:"Pages par jour"}).catch(writeErr);};''')
R('''      await S.db.doc("projects/"+S.pid).update({pagesPerDay:t8/8});''', '''      await trk("projects/"+S.pid).update({pagesPerDay:t8/8});''')
t = re.sub(r'const APP_VERSION="1\.21\.\d";', 'const APP_VERSION="1.22.0";', t)
open(p, "w", encoding="utf-8").write(t); print("ok", p)
