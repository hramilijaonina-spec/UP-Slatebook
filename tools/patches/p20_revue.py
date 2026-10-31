# Revue ergonomique : téléphone, simplification, ergonomie, technique.
import re, sys
p = sys.argv[1]; t = open(p, encoding="utf-8").read()
def R(a, b, n=1):
    global t
    c = t.count(a)
    assert c == n, (a[:90], c)
    t = t.replace(a, b)
def between(a, b):
    i = t.index(a); j = t.index(b, i); return i, j

UNDO_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 14 4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 0 11H11"/></svg>'
REDO_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m15 14 5-5-5-5"/><path d="M20 9H9.5a5.5 5.5 0 0 0 0 11H13"/></svg>'

# ================= EN-TÊTE : recherche, pastille « local », bandeau refermable =================
R('''  <button class="menubtn" id="b-menu" type="button" aria-label="Menu" aria-haspopup="menu" aria-expanded="false"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
  <div class="spacer"></div>''', '''  <button class="menubtn" id="b-menu" type="button" aria-label="Menu" aria-haspopup="menu" aria-expanded="false"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
  <button class="menubtn" id="b-search" type="button" aria-label="Rechercher dans le projet" title="Rechercher (⌘K)"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6"/><path d="m15 15 5.5 5.5"/></svg></button>
  <span class="localpill" id="localpill" hidden title="Mode local : ouvre cette page sur claude.ai pour partager les projets avec ton équipe. Rien n'est enregistré ici.">Local</span>
  <div class="spacer"></div>''')
R('''  if(S.local)showBanner("Mode local : ouvre cette page sur claude.ai pour partager les projets avec ton équipe. Rien n'est enregistré ici.");''',
  '''  if(S.local){const lp=$("#localpill");if(lp){lp.hidden=false;lp.onclick=()=>toast(lp.title,6000);}}''')
R('''function showBanner(t){const b=$("#banner");b.textContent=t;b.hidden=false;}''',
  '''function showBanner(t){const b=$("#banner");b.innerHTML=`<span>${esc(t)}</span><button type="button" class="banner-x" aria-label="Fermer le message">×</button>`;b.hidden=false;b.querySelector(".banner-x").onclick=()=>{b.hidden=true;};}''')

# ================= MENU : tout le projet sous PROJET (plus de •••) =================
R('''      ${S.canWrite&&cur?`<button class="btn ghost small" id="projmenu" aria-label="Options du projet">•••</button>`:""}`;''', '''`;''')
R('''    const pm=$("#projmenu");if(pm)pm.onclick=e=>projectMenu(e.currentTarget);
''', '')
i, j = between('  const sub=[];\n  if(S.canWrite)sub.push(["new","Nouveau projet"]);', '  const draw=()=>{')
t = t[:i] + '''  const sub=[];const cp=S.pid&&!S.home?P():null;
  if(S.canWrite)sub.push(["new","Nouveau projet"]);
  if(cp&&S.canWrite&&!S.aiOff)sub.push(["ai","Analyser tout avec l'IA"+(todo?" · "+todo+" scène"+(todo>1?"s":""):"")]);
  if(cp)sub.push(["export","Exporter…"]);
  if(cp)sub.push(["-"],["versions","Historique des versions"]);
  if(cp&&S.canWrite)sub.push(["bump","Nouvelle version ("+verTag(cp)+" → v"+nextVer(cp)+")…"],["rename","Renommer le projet"],["backup","Sauvegarder le projet (fichier)"],["restore","Restaurer une sauvegarde…"],["clean","Retirer un texte de toutes les scènes"]);
  if(cp&&S.isAdmin)sub.push(["-"],["delete","Supprimer le projet"]);
''' + t[j:]
R('''<div class="mm-sub"${mmProjOpen?"":" hidden"}>${sub.map(([k,l])=>`<button type="button" role="menuitem" data-a="${k}">${esc(l)}</button>`).join("")||''',
  '''<div class="mm-sub"${mmProjOpen?"":" hidden"}>${sub.map(([k,l])=>k==="-"?`<hr>`:`<button type="button" role="menuitem" data-a="${k}"${k==="delete"?' class="danger"':""}>${esc(l)}</button>`).join("")||''')
R('''      else if(k==="export")exportMenu(anchor);
      else if(k==="versions")openVersions();
      else if(k==="options")projectMenu(anchor);});};''', '''      else if(k==="export")openExport();
      else if(k==="versions")openVersions();
      else if(k==="bump")bumpVersion();
      else if(k==="rename")renameProject();
      else if(k==="backup")backupProject();
      else if(k==="restore")openRestore();
      else if(k==="clean")cleanupText();
      else if(k==="delete")confirmDelete();});};''')

# ================= ÉCRAN « EXPORTER » unique =================
R('''function exportMenu(anchor){
  openPop(anchor.getBoundingClientRect(),"Exporter",[''', '''function exportMenu(){openExport();}
function openExport(focus){
  if(!S.pid){toast("Ouvre d'abord un projet.");return;}
  if(!S.dl){toast("L'export n'est pas disponible ici.");return;}
  const has=S.shots.some(x=>!isOpt(x));const p=P();
  const sec=(k,title,items)=>`<section class="ex-sec${focus===k?" focus":""}" data-k="${k}"><h4>${title}</h4><div class="ex-btns">${items.map(([id,l,dis])=>`<button type="button" class="btn" data-x="${id}" ${dis?"disabled":""}>${l}</button>`).join("")}</div></section>`;
  const m=modal(`<h3>Exporter · ${esc(p?.name||"")}</h3>
    <div class="ex">
    ${sec("script","Scénario",[["s-pdf","PDF"],["s-fdx","Final Draft (.fdx)"],["s-fountain","Fountain"]])}
    ${sec("dec","Découpage technique <small>sans les plans optionnels</small>",[["d-pdf","PDF paysage",!has],["d-pptx","PowerPoint paysage",!has],["d-csv","CSV pour Excel",!has]])}
    ${sec("dep","Dépouillement",[["e-sheets","Fiches imprimables"],["e-csv","Liste des éléments (CSV)"]])}
    ${sec("plan","Plan de travail",[["p-html","Plan imprimable"],["p-csv","CSV pour Excel"]])}
    ${sec("proj","Projet complet",[["j-json","Sauvegarde (fichier .json)"]])}
    </div>
    <div class="mfoot"><button class="btn primary" id="ex-c">Fermer</button></div>`);
  m.querySelector(".modal").style.maxWidth="640px";
  const run={"s-pdf":exportScriptPDF,"s-fdx":exportFDX,"s-fountain":exportFountain,"d-pdf":()=>runDecExport("pdf"),"d-pptx":()=>runDecExport("pptx"),"d-csv":exportDecCSV,
    "e-sheets":exportSheets,"e-csv":exportCSV,"p-html":exportPlanHTML,"p-csv":exportPlanCSV,"j-json":backupProject};
  m.querySelectorAll("[data-x]").forEach(b=>b.onclick=()=>{m.remove();run[b.dataset.x]();});
  m.querySelector("#ex-c").onclick=()=>m.remove();
  m.querySelector(".ex-sec.focus")?.scrollIntoView({block:"nearest"});
}
function exportMenuOld(anchor){
  openPop(anchor.getBoundingClientRect(),"Exporter",[''')
R('''  $("#ed-export").onclick=e=>scriptExportMenu(e.currentTarget);''', '''  $("#ed-export").onclick=()=>openExport("script");''')
i, j = between('''    ${S.dl?`<div class="dcm-ex"><span class="dc-lbl">Exporter · sans les plans optionnels</span>''', '''<button class="btn small" type="button" data-ex="csv" ${has?"":"disabled"}>CSV pour Excel</button></div>`:""}''')
j = t.index('`:""}', j) + len('`:""}')
t = t[:i] + '''    ${S.dl?`<div class="dcm-ex"><button class="btn small" type="button" data-ex="all">Exporter le découpage…</button></div>`:""}''' + t[j:]
R('''d.querySelectorAll("[data-ex]").forEach(b=>b.onclick=()=>{saveT();closeDcPop();const k=b.dataset.ex;if(k==="csv")exportDecCSV();else runDecExport(k);});''',
  '''d.querySelectorAll("[data-ex]").forEach(b=>b.onclick=()=>{saveT();closeDcPop();openExport("dec");});''')

# ================= ACCUEIL unique (aussi quand il n'y a encore aucun projet) =================
R('''  if(!S.pid&&!S.projects.length){desk.innerHTML=welcomeHTML();bindWelcome();return;}
''', '')
R('''      </div>`;}).join("")||`<p class="empty">Aucun projet pour l'instant.</p>`}</div>
  </div></div>`;''', '''      </div>`;}).join("")||""}</div>
    ${groups.length?"":`<div class="home-empty"><p>Importe un scénario en PDF, Word converti en PDF, Final Draft ou texte. L'outil le découpe en scènes, l'IA repère rôles, accessoires, costumes et véhicules, puis toute l'équipe corrige et commente en direct.</p>
      <div class="steps"><div><b>1 · Importer</b>PDF, .fdx, .fountain ou texte collé, même écrit « en prose ».</div><div><b>2 · Découper</b>Plan par plan, à la main ou avec l'IA.</div><div><b>3 · Organiser</b>Dépouillement, plan de travail, suivi du tournage.</div></div>
      ${S.canWrite?`<div class="home-acts"><button class="btn" id="h-example">Essayer avec un exemple</button></div>`:`<p>Aucun projet pour l'instant. Une personne avec le rôle Éditeur doit en créer un.</p>`}</div>`}
  </div></div>`;''')
R('''    <h2 class="label">Derniers projets</h2>''', '''    ${groups.length?`<h2 class="label">Derniers projets</h2>`:""}''')
R('''  const n=$("#h-new");if(n)n.onclick=()=>openImport();const r=$("#h-restore");if(r)r.onclick=openRestore;''',
  '''  const n=$("#h-new");if(n)n.onclick=()=>openImport();const r=$("#h-restore");if(r)r.onclick=openRestore;
  const ex=$("#h-example");if(ex)ex.onclick=()=>openImport(EXAMPLE,"Le Collier (exemple)");''')
R('''<span class="label">UP Slatebook</span><h1>Accueil</h1>''', '''<span class="label">UP Slatebook · préproduction</span><h1>${S.projects.length?"Accueil":"Bienvenue"}</h1>''')

# ================= HISTORIQUE : nom plus clair =================
R('''  const m=modal(`<h3>Versions · ${esc(p.name||"Projet")}</h3>''', '''  const m=modal(`<h3>Historique des versions · ${esc(p.name||"Projet")}</h3>''')
R('''title="Versions et sauvegardes du projet"''', '''title="Historique des versions du projet"''')

# ================= ANNULER / RÉTABLIR dans le plan de travail et le dépouillement =================
R('''    const arr=col==="shots"?S.shots:col==="scenes"?S.scenes:col==="backups"?S.backups:null;''',
  '''    const arr=col==="shots"?S.shots:col==="scenes"?S.scenes:col==="backups"?S.backups:col==="elements"?S.elements:col==="days"?S.days:col==="locations"?S.locations:null;''')
R('''function hButtons(){
  const u=$("#dc-undo"),r=$("#dc-redo");const lu=H.undo[H.undo.length-1],lr=H.redo[H.redo.length-1];
  if(u){u.disabled=!lu||H.busy||!!H.grp;u.title=lu?"Annuler : "+lu.label+" (⌘Z)":"Rien à annuler";}
  if(r){r.disabled=!lr||H.busy||!!H.grp;r.title=lr?"Rétablir : "+lr.label+" (⇧⌘Z)":"Rien à rétablir";}
}''', '''function hButtons(){
  const lu=H.undo[H.undo.length-1],lr=H.redo[H.redo.length-1];
  document.querySelectorAll("#dc-undo,.h-undo").forEach(u=>{u.disabled=!lu||H.busy||!!H.grp;u.title=lu?"Annuler : "+lu.label+" (⌘Z)":"Rien à annuler";});
  document.querySelectorAll("#dc-redo,.h-redo").forEach(r=>{r.disabled=!lr||H.busy||!!H.grp;r.title=lr?"Rétablir : "+lr.label+" (⇧⌘Z)":"Rien à rétablir";});
}
document.addEventListener("click",e=>{const b=e.target.closest?.(".h-undo,.h-redo");if(!b||b.disabled)return;if(b.classList.contains("h-undo"))hUndo();else hRedo();});''')
R('''  if(S.tab!=="dec"||!S.pid||!S.canWrite||document.querySelector(".scrim"))return;
  const mod=e.metaKey||e.ctrlKey;if(!mod)return;const k=e.key.toLowerCase();''', '''  if(!["dec","scenes","plan"].includes(S.tab)||S.home||!S.pid||!S.canWrite||document.querySelector(".scrim"))return;
  const mod=e.metaKey||e.ctrlKey;if(!mod)return;const k=e.key.toLowerCase();''')
# écritures suivies (donc annulables)
R('''function updateScene(sid,patch){return S.db.doc(base()+"/scenes/"+sid).update({...patch,updatedAt:Date.now(),updatedBy:S.me?.id||null}).catch(writeErr);}''',
  '''function updateScene(sid,patch,label){return trk(base()+"/scenes/"+sid).update({...patch,updatedAt:Date.now(),updatedBy:S.me?.id||null},{label:label||"Scène "+(scene(sid)?.num||"")}).catch(writeErr);}''')
R('''  const p=S.db.collection(base()+"/elements").add({sceneId:sid,cat,name:name.trim().slice(0,120),src,by:S.me?.id||null,at:Date.now()}).catch(writeErr);
  if(s&&(s.status||"todo")==="todo")updateScene(sid,{status:"ai"});
  return p;''', '''  return hGroup("Ajouter « "+name.trim()+" »",async()=>{
    await trk(base()+"/elements/"+uid()).set({sceneId:sid,cat,name:name.trim().slice(0,120),src,by:S.me?.id||null,at:Date.now()},{before:null}).catch(writeErr);
    if(s&&(s.status||"todo")==="todo")await updateScene(sid,{status:"ai"});});''')
R('''    ...CATS.filter(c=>c.id!==e.cat).map(c=>({label:"Déplacer vers "+c.label,color:c.color,run:()=>S.db.doc(base()+"/elements/"+e.id).update({cat:c.id}).catch(writeErr)})),
    {label:"Retirer de la scène",danger:true,run:()=>S.db.doc(base()+"/elements/"+e.id).delete().catch(writeErr)}]);''',
  '''    ...CATS.filter(c=>c.id!==e.cat).map(c=>({label:"Déplacer vers "+c.label,color:c.color,run:()=>trk(base()+"/elements/"+e.id).update({cat:c.id},{label:"« "+e.name+" » → "+c.label}).catch(writeErr)})),
    {label:"Retirer de la scène",danger:true,run:()=>trk(base()+"/elements/"+e.id).delete({label:"Retirer « "+e.name+" »"}).catch(writeErr)}]);''')
R('''async function moveScenes(sids,dayId,beforeSid){
  try{''', '''async function moveScenes(sids,dayId,beforeSid){
  const lab=(dayId?"Placer ":"Retirer ")+(sids.length>1?sids.length+" scènes":"la scène "+(scene(sids[0])?.num||""));
  return hGroup(lab,()=>moveScenesRaw(sids,dayId,beforeSid));
}
async function moveScenesRaw(sids,dayId,beforeSid){
  try{''')
R('''    if(!dayId){await chunked(sids,5,sid=>S.db.doc(base()+"/scenes/"+sid).update({dayId:null,dayPos:null}));return;}''',
  '''    if(!dayId){await chunked(sids,5,sid=>trk(base()+"/scenes/"+sid).update({dayId:null,dayPos:null}));return;}''')
R('''({sid,pos})=>S.db.doc(base()+"/scenes/"+sid).update({dayId,dayPos:pos}));''', '''({sid,pos})=>trk(base()+"/scenes/"+sid).update({dayId,dayPos:pos}));''')
R('''  try{const ref=S.db.collection(base()+"/days").doc();await ref.set({order:max+1,date:nextDate(),createdAt:Date.now()});return ref.id;}catch(e){writeErr(e);return null;}''',
  '''  try{const id=uid();await trk(base()+"/days/"+id).set({order:max+1,date:nextDate(),createdAt:Date.now()},{before:null,label:"Nouvelle journée"});return id;}catch(e){writeErr(e);return null;}''')
R('''  try{await chunked(days.map((d,k)=>({d,o:k===i?j:k===j?i:k})),5,({d,o})=>d.order===o+1?null:S.db.doc(base()+"/days/"+d.id).update({order:o+1}));}catch(e){writeErr(e);}''',
  '''  try{await hGroup("Déplacer J"+(i+1),()=>chunked(days.map((d,k)=>({d,o:k===i?j:k===j?i:k})),5,({d,o})=>d.order===o+1?null:trk(base()+"/days/"+d.id).update({order:o+1})));}catch(e){writeErr(e);}''')
R('''  try{await chunked(sc,5,s=>S.db.doc(base()+"/scenes/"+s.id).update({dayId:null,dayPos:null}));await S.db.doc(base()+"/days/"+did).delete();''',
  '''  try{await hGroup("Supprimer J"+(i+1),async()=>{await chunked(sc,5,s=>trk(base()+"/scenes/"+s.id).update({dayId:null,dayPos:null}));await trk(base()+"/days/"+did).delete();});''')
R('''  box.querySelectorAll(".ddate").forEach(i=>i.onchange=()=>S.db.doc(base()+"/days/"+i.dataset.did).update({date:i.value||""}).catch(writeErr));''',
  '''  box.querySelectorAll(".ddate").forEach(i=>i.onchange=()=>trk(base()+"/days/"+i.dataset.did).update({date:i.value||""},{label:"Date de la journée"}).catch(writeErr));''')
# « Proposer un plan » : un seul retour en arrière
R('''    go.disabled=true;go.textContent="Création…";
    try{
      const all=md==="all";''', '''    go.disabled=true;go.textContent="Création…";
    try{await hGroup("Proposer un plan",async()=>{
      const all=md==="all";''')
R('''      if(all){await chunked(S.scenes.filter(s=>s.dayId),5,s=>S.db.doc(base()+"/scenes/"+s.id).update({dayId:null,dayPos:null}));await chunked([...S.days],5,x=>S.db.doc(base()+"/days/"+x.id).delete());order=0;}''',
  '''      if(all){await chunked(S.scenes.filter(s=>s.dayId),5,s=>trk(base()+"/scenes/"+s.id).update({dayId:null,dayPos:null}));await chunked([...S.days],5,x=>trk(base()+"/days/"+x.id).delete());order=0;}''')
R('''        await chunked(S.scenes.filter(s=>s.dayId&&!s.filmed),5,s=>S.db.doc(base()+"/scenes/"+s.id).update({dayId:null,dayPos:null}));
        await chunked(S.days.filter(d=>!keepIds.has(d.id)),5,x=>S.db.doc(base()+"/days/"+x.id).delete());''',
  '''        await chunked(S.scenes.filter(s=>s.dayId&&!s.filmed),5,s=>trk(base()+"/scenes/"+s.id).update({dayId:null,dayPos:null}));
        await chunked(S.days.filter(d=>!keepIds.has(d.id)),5,x=>trk(base()+"/days/"+x.id).delete());''')
R('''      for(const ids of plan){const ref=S.db.collection(base()+"/days").doc();order++;
        await ref.set({order,date:date||"",createdAt:Date.now()});
        await chunked(ids.map((sid,i)=>({sid,i})),5,({sid,i})=>S.db.doc(base()+"/scenes/"+sid).update({dayId:ref.id,dayPos:(i+1)*1024}));''',
  '''      for(const ids of plan){const did=uid();order++;
        await trk(base()+"/days/"+did).set({order,date:date||"",createdAt:Date.now()},{before:null});
        await chunked(ids.map((sid,i)=>({sid,i})),5,({sid,i})=>trk(base()+"/scenes/"+sid).update({dayId:did,dayPos:(i+1)*1024}));''')
R('''      m.remove();toast(plan.length+" journée"+''', '''      });m.remove();toast(plan.length+" journée"+''')
# boutons dans le plan de travail et le dépouillement
R('''      ${alerts.length?`<span class="st ai" title="Rôles convoqués sur des jours non consécutifs : voir le menu">''',
  '''      ${S.canWrite?`<button class="menubtn h-undo" type="button" aria-label="Annuler">''' + UNDO_SVG + '''</button><button class="menubtn h-redo" type="button" aria-label="Rétablir">''' + REDO_SVG + '''</button>`:""}
      ${alerts.length?`<span class="st ai" title="Rôles convoqués sur des jours non consécutifs : voir le menu">''')
R('''      <button class="btn ghost small" id="b-prev" aria-label="Scène précédente">←</button><button class="btn ghost small" id="b-next" aria-label="Scène suivante">→</button>''',
  '''      ${S.canWrite?`<button class="btn ghost small icbtn h-undo" type="button" aria-label="Annuler">''' + UNDO_SVG + '''</button><button class="btn ghost small icbtn h-redo" type="button" aria-label="Rétablir">''' + REDO_SVG + '''</button>`:""}
      <button class="btn ghost small" id="b-prev" aria-label="Scène précédente">←</button><button class="btn ghost small" id="b-next" aria-label="Scène suivante">→</button>''')
R('''  box.querySelectorAll(".d-donecb").forEach(c=>{c.indeterminate=c.dataset.part==="1";});''', '''  box.querySelectorAll(".d-donecb").forEach(c=>{c.indeterminate=c.dataset.part==="1";});hButtons();''')
R('''  $("#page").querySelectorAll("mark.hl").forEach(m=>m.onclick=ev=>{if(!S.canWrite)return;const e=S.elements.find(x=>x.id===m.dataset.eid);if(e)elementMenu(e,m);});
  findApply(false);''', '''  $("#page").querySelectorAll("mark.hl").forEach(m=>m.onclick=ev=>{if(!S.canWrite)return;const e=S.elements.find(x=>x.id===m.dataset.eid);if(e)elementMenu(e,m);});
  findApply(false);hButtons();''')

# ================= RECHERCHE ⌘K =================
R('''/* ---------- accueil : derniers projets ---------- */''', '''/* ---------- recherche dans le projet (⌘K) ---------- */
function openSearch(){
  if(document.querySelector(".srch"))return;
  const m=modal(`<div class="srch"><input type="search" id="sq" placeholder="${S.pid&&!S.home?"Scène, personnage, accessoire, plan…":"Nom du projet…"}" aria-label="Rechercher" autocomplete="off"><div class="sr" id="sr" role="listbox"></div><p class="empty sr-hint">↑ ↓ pour choisir · Entrée pour ouvrir · Échap pour fermer</p></div>`);
  m.querySelector(".modal").classList.add("srch-m");
  const q=m.querySelector("#sq"),box=m.querySelector("#sr");let res=[],sel=0;
  const hit=(txt,k)=>{const n=norm(txt);const i=n.indexOf(k);return i<0?null:String(txt).slice(Math.max(0,i-30),i+k.length+50).replace(/\\s+/g," ");};
  const run=()=>{const k=norm(q.value);res=[];
    if(!S.pid||S.home){for(const g of seriesGroups())if(!k||norm(g.name).includes(k))res.push({kind:"Projet",title:g.name||"Sans titre",sub:g.items.length>1?g.items.length+" épisodes":"",go:()=>openProject(g.items[0].id)});}
    else if(k.length>=2){
      for(const s of S.scenes){const h=norm(s.num+" "+s.heading).includes(k)?"":hit((s.synopsis||"")+" "+(s.body||""),k);
        if(norm(s.num+" "+s.heading).includes(k)||h)res.push({kind:"Scène",title:s.num+" · "+s.heading,sub:h||"",go:()=>{leaveHome();S.tab="scenes";$("#desk").innerHTML="";selectScene(s.id);}});}
      const seen=new Set();
      for(const e of S.elements){if(!norm(e.name).includes(k))continue;const s=scene(e.sceneId);if(!s)continue;const key=e.id;if(seen.has(key))continue;seen.add(key);
        res.push({kind:CAT[e.cat]?.label||"Élément",color:CAT[e.cat]?.color,title:e.name,sub:"scène "+s.num+" · "+s.heading,go:()=>{leaveHome();S.tab="scenes";$("#desk").innerHTML="";selectScene(s.id);setTimeout(()=>findStart(e.id),250);}});}
      for(const x of S.shots){const h=hit((x.action||"")+" "+(x.sound||"")+" "+(x.notes||""),k);if(!h)continue;const s=scene(x.sceneId);
        res.push({kind:"Plan",title:"Plan "+shotNum(x)+(s?" · "+s.heading:""),sub:h,go:()=>{leaveHome();goTab("dec");setTimeout(()=>{const r=document.getElementById("dc-"+x.id);if(r){r.scrollIntoView({block:"center"});r.classList.add("dc-flash");setTimeout(()=>r.classList.remove("dc-flash"),1300);}},400);}});}
    }
    res=res.slice(0,60);sel=0;draw();};
  const draw=()=>{box.innerHTML=res.length?res.map((r,i)=>`<button type="button" role="option" class="sr-i" data-i="${i}" aria-selected="${i===sel}"><span class="sr-k"${r.color?` style="--c:${r.color}"`:""}>${esc(r.kind)}</span><span class="sr-t"><b>${esc(r.title)}</b>${r.sub?`<small>${esc(r.sub)}</small>`:""}</span></button>`).join("")
      :`<p class="empty" style="padding:10px">${q.value.trim().length<2&&S.pid&&!S.home?"Tape au moins 2 lettres.":"Aucun résultat."}</p>`;
    box.querySelectorAll(".sr-i").forEach(b=>b.onclick=()=>pick(+b.dataset.i));};
  const pick=i=>{const r=res[i];if(!r)return;m.remove();r.go();};
  q.oninput=run;q.onkeydown=e=>{if(e.key==="ArrowDown"||e.key==="ArrowUp"){e.preventDefault();if(!res.length)return;sel=(sel+(e.key==="ArrowDown"?1:-1)+res.length)%res.length;draw();box.querySelector('[aria-selected="true"]')?.scrollIntoView({block:"nearest"});}
    else if(e.key==="Enter"){e.preventDefault();pick(sel);}};
  run();q.focus();
}
document.addEventListener("keydown",e=>{if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==="k"&&S.projectsLoaded){e.preventDefault();openSearch();}});
/* ---------- accueil : derniers projets ---------- */''')

# ================= DÉPOUILLEMENT AU DOIGT : toucher un mot pour l'ajouter =================
R('''  pane.addEventListener("mouseup",()=>setTimeout(handler,10));
  pane.addEventListener("touchend",()=>setTimeout(handler,350));''', '''  pane.addEventListener("mouseup",()=>setTimeout(handler,10));
  let tapAt=0,skipTap=false;
  /* un appui qui sert à refermer un menu ou la liste des scènes n'ouvre pas l'ajout */
  window.addEventListener("pointerdown",()=>{skipTap=!!(popEl||S.listOpen||document.querySelector(".dc-pop"));},true);
  pane.addEventListener("touchend",()=>setTimeout(()=>{if(Date.now()-tapAt>700)handler();},350));
  /* téléphone : un appui sur un mot le sélectionne et propose de l'ajouter ; on peut ensuite étendre la sélection avec les poignées */
  pane.addEventListener("click",e=>{
    if(!S.canWrite||skipTap||!matchMedia("(pointer:coarse)").matches)return;
    const page=$("#page");if(!page||!page.contains(e.target)||e.target.closest("mark,button,a"))return;
    const sel=getSelection();if(sel&&!sel.isCollapsed)return;
    let node,off;
    if(document.caretPositionFromPoint){const cp=document.caretPositionFromPoint(e.clientX,e.clientY);if(cp){node=cp.offsetNode;off=cp.offset;}}
    else if(document.caretRangeFromPoint){const cr=document.caretRangeFromPoint(e.clientX,e.clientY);if(cr){node=cr.startContainer;off=cr.startOffset;}}
    if(!node||node.nodeType!==3)return;
    const txt=node.textContent;const W=/[\\p{L}\\p{N}'’-]/u;let a=off,b=off;
    while(a>0&&W.test(txt[a-1]))a--;while(b<txt.length&&W.test(txt[b]))b++;
    if(b-a<2)return;
    const r=document.createRange();r.setStart(node,a);r.setEnd(node,b);sel.removeAllRanges();sel.addRange(r);tapAt=Date.now();handler();
  });''')
R('''"Sélectionne un mot ou une expression dans le texte pour l'ajouter au dépouillement. Clique sur un passage surligné pour le modifier, ou sur un élément de la fiche pour retrouver ses passages."''',
  '''(matchMedia("(pointer:coarse)").matches?"Touche un mot pour l'ajouter au dépouillement (étire la sélection pour plusieurs mots). Touche un passage surligné pour le modifier, ou un élément de la fiche pour retrouver ses passages.":"Sélectionne un mot ou une expression dans le texte pour l'ajouter au dépouillement. Clique sur un passage surligné pour le modifier, ou sur un élément de la fiche pour retrouver ses passages.")''')

# ================= PASTILLE D'AVANCEMENT, la même dans tous les onglets =================
R('''function renderListKeepFocus(){''', '''/* avancement d'une scène : D dépouillement · plans faits / plans · T tournée */
function progHTML(s){
  const st=s.status||"todo";const sh=shotsOf(s.id).filter(x=>!isOpt(x));const done=sh.filter(x=>x.done).length;
  return `<span class="prog" title="Dépouillement : ${STATUS[st]} · plans faits : ${done}/${sh.length} · ${s.filmed?"tournée":"pas encore tournée"}"><i class="pg-d ${st}">D</i><i class="pg-p${sh.length&&done===sh.length?" ok":""}">${sh.length?done+"/"+sh.length:"0"}</i><i class="pg-t${s.filmed?" ok":""}">T</i></span>`;
}
function renderListKeepFocus(){''')
R('''<span>${elCount[s.id]||0} élém.</span>''', '''<span>${elCount[s.id]||0} élém.</span>${progHTML(s)}''')
R('''      <span class="sub">${esc([s.intExt,s.time].filter(Boolean).join(" · "))}${lieu?` · <b>${esc(lieu.name)}</b>`:""}</span>''',
  '''      <span class="sub">${progHTML(s)} ${esc([s.intExt,s.time].filter(Boolean).join(" · "))}${lieu?` · <b>${esc(lieu.name)}</b>`:""}</span>''')
i = t.index('const seq=`<td class="dct-seq" rowspan="${rows}"><b>${esc(s.num)}</b><span class="h">${esc(s.heading)}</span><small>')
j = t.index('</small>', i) + len('</small>')
t = t[:j] + '${progHTML(s)}' + t[j:]

# ================= DURÉE dans le plan de travail =================
R('''const targetE8=()=>Math.round((Number(P()?.pagesPerDay)||4)*8);''', '''const targetE8=()=>Math.round((Number(P()?.pagesPerDay)||4)*8);
/* durée estimée d'après le découpage (plans optionnels exclus) */
const sceneDur=s=>sumDur(shotsOf(s.id).filter(x=>!isOpt(x)));
const scenesDur=list=>list.reduce((a,s)=>a+sceneDur(s),0);''')
R('''            <span class="dmeta"><b>${fmtE(e8)} p.</b>${lieux.length?" · "+esc(lieux.join(" · ")):""}</span>''',
  '''            <span class="dmeta">${scenesDur(sc)?`<b>≈ ${fmtDur(scenesDur(sc))}</b> · `:""}<b>${fmtE(e8)} p.</b>${lieux.length?" · "+esc(lieux.join(" · ")):""}</span>''')
R('''      <div class="stat"><b>${fmtE(planned)}<small> / ${fmtE(tot)}</small></b><span>pages planifiées</span></div>''',
  '''      ${scenesDur(S.scenes)?`<div class="stat"><b>${fmtDur(scenesDur(S.scenes.filter(isPlanned)))}<small> / ${fmtDur(scenesDur(S.scenes))}</small></b><span>durée planifiée</span></div>`:""}
      <div class="stat"><b>${fmtE(planned)}<small> / ${fmtE(tot)}</small></b><span>pages planifiées</span></div>''')

# ================= DÉCOUPAGE : étiquettes pour la vue en cartes =================
R('''    <td class="ed dct-desc">${ta(''', '''    <td class="ed dct-desc" data-l="Description">${ta(''')
R('''    <td class="ed dct-audio"><div class="dc-hl">''', '''    <td class="ed dct-audio" data-l="Audio"><div class="dc-hl">''')
R('''    <td class="ed dct-notes">${ta(''', '''    <td class="ed dct-notes" data-l="Notes">${ta(''')

# ================= FLUIDITÉ : ne redessiner que si quelque chose a changé =================
R('''function renderPlan(){
  const box=$("#plan");if(!box||!S.pid)return;''', '''function planSig(){
  const pick=(a,f)=>a.map(x=>f.map(k=>x[k]));
  return JSON.stringify([S.pid,S.canWrite,S.planGroup,S.poolOpen,matchMedia("(max-width:1150px)").matches,[...planOpenSet()],P()?.pagesPerDay,
    pick(S.days,["id","order","date"]),pick(S.scenes,["id","num","heading","location","intExt","time","dayNight","eighths","dayId","dayPos","filmed","status"]),
    pick(S.locations,["id","name","address","decors"]),pick(S.elements.filter(e=>e.cat==="cast"),["id","sceneId","name"]),pick(S.shots,["id","sceneId","dur","done","pos"])]);
}
function renderPlan(){
  const box=$("#plan");if(!box||!S.pid)return;
  const sig=planSig();if(box.dataset.sig===sig&&box.childElementCount){hButtons();return;}box.dataset.sig=sig;''')
R('''function renderScene(){
  const pane=$("#scriptpane");if(!pane)return;
  const s=scene(S.sid);''', '''function renderScene(){
  const pane=$("#scriptpane");if(!pane)return;
  const s=scene(S.sid);
  if(s){const sig=JSON.stringify([s,elsOf(s.id),S.analyzing.has(s.id),S.canWrite,S.aiOff,!!S.busy,S.scenes.indexOf(s),S.scenes.length,shotsOf(s.id).map(x=>[x.dur,x.done])]);
    if(pane.dataset.sig===sig&&pane.childElementCount){findApply(false);hButtons();return;}pane.dataset.sig=sig;}''')

# ================= PHOTOS DES PLANS DANS L'HISTORIQUE =================
R('''    const pid=S.pid,bs=base();const id=Date.now().toString(36)+uid().slice(0,4);''', '''    const pid=S.pid,bs=base();const id=Date.now().toString(36)+uid().slice(0,4);
    await snapSaveImages(bs);''')
R('''async function snapPrune(keepId){''', '''/* les photos des plans (gardées dans le plan lui-même) sont rangées une fois, à part, pour pouvoir revenir à une version avec ses photos */
async function snapSaveImages(bs){
  SNAP.imgs=SNAP.imgs||new Set();
  for(const x of S.shots){const v=String(x.img||"");if(!/^data:image\\//.test(v)||v.length>240000)continue;const h=snapHash(v);if(SNAP.imgs.has(h))continue;
    try{const r=await S.db.doc(bs+"/snapimgs/"+h).get();if(!r.exists)await S.db.doc(bs+"/snapimgs/"+h).set({d:v});SNAP.imgs.add(h);}catch{}}
}
async function snapLoadImage(h){try{const r=await S.db.doc(base()+"/snapimgs/"+h).get();return r.exists?r.data().d||null:null;}catch{return null;}}
async function snapPrune(keepId){''')
R('''        if(col==="shots"&&typeof doc.img==="string"&&doc.img.startsWith("@keep:"))doc.img=c&&c.img&&snapHash(String(c.img))===doc.img.slice(6)?c.img:(c?.img||null);''',
  '''        if(col==="shots"&&typeof doc.img==="string"&&doc.img.startsWith("@keep:")){const h=doc.img.slice(6);doc.img=c&&c.img&&snapHash(String(c.img))===h?c.img:((await snapLoadImage(h))||c?.img||null);}''')

# ================= STYLES =================
R('/* menu principal */', '''/* en-tête : recherche, mode local, bandeau */
.localpill{font-size:11px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;padding:2px 8px;border-radius:10px;border:1px solid color-mix(in srgb,var(--warn) 55%,var(--line));color:var(--warn);cursor:help;white-space:nowrap}
.banner{display:flex;align-items:center;gap:10px}.banner span{flex:1;min-width:0}
.banner-x{flex:0 0 auto;border:0;background:transparent;color:var(--fg);font-size:20px;line-height:1;width:30px;height:30px;border-radius:6px}
.banner-x:hover{background:var(--surface)}
.mm-sub hr{border:0;border-top:1px solid var(--line);margin:4px 0}
.mm-sub button.danger{color:var(--danger)}
/* écran Exporter */
.ex{display:flex;flex-direction:column;gap:10px;max-height:min(70vh,620px);overflow:auto}
.ex-sec{border:1px solid var(--line);border-radius:var(--r);padding:10px 12px}
.ex-sec.focus{border-color:var(--accent);background:var(--accent-soft)}
.ex-sec h4{margin:0 0 8px;font-family:var(--f-display);font-size:16px;text-transform:uppercase;letter-spacing:.03em}
.ex-sec h4 small{font-family:var(--f-ui);font-size:11.5px;text-transform:none;letter-spacing:0;color:var(--muted);font-weight:500}
.ex-btns{display:flex;flex-wrap:wrap;gap:6px}
/* recherche */
.srch-m{max-width:620px!important;padding:12px!important}
.srch{display:flex;flex-direction:column;gap:8px}
.srch input{width:100%;font-size:16px;padding:10px 12px;background:var(--sunk);border:1px solid var(--line-strong);border-radius:8px;color:var(--fg)}
.sr{display:flex;flex-direction:column;max-height:min(60vh,520px);overflow:auto}
.sr-i{display:grid;grid-template-columns:96px minmax(0,1fr);gap:10px;align-items:start;text-align:left;border:0;background:transparent;padding:8px;border-radius:6px;color:var(--fg)}
.sr-i[aria-selected=true],.sr-i:hover{background:var(--sunk)}
.sr-k{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;color:var(--c,var(--muted));padding-top:2px}
.sr-t b{display:block;font-size:13.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sr-t small{display:block;color:var(--muted);font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sr-hint{margin:0;font-size:11.5px}
/* pastille d'avancement */
.prog{display:inline-flex;gap:3px;vertical-align:middle}
.prog i{font-style:normal;font-size:10px;font-weight:700;padding:0 5px;border-radius:8px;border:1px solid var(--line-strong);color:var(--muted);line-height:15px;font-variant-numeric:tabular-nums}
.prog i.ok,.prog .pg-d.ok{color:var(--ok);border-color:color-mix(in srgb,var(--ok) 60%,var(--line));background:color-mix(in srgb,var(--ok) 14%,transparent)}
.prog .pg-d.ai{color:var(--warn);border-color:color-mix(in srgb,var(--warn) 55%,var(--line))}
.dct-seq .prog{margin-top:6px;display:flex}
.home-empty{display:flex;flex-direction:column;gap:12px;color:var(--muted)}
.home-empty p{margin:0;max-width:62ch}
.icbtn svg,.menubtn.h-undo svg,.menubtn.h-redo svg{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.menubtn:disabled{opacity:.4}
/* ---------- téléphone ---------- */
@media (max-width:760px){
  .top{flex-wrap:nowrap;gap:6px;padding-block:6px}
  .brand{font-size:18px;gap:6px;min-width:0}
  .brand .logo{font-size:14px;height:22px}
  .brand .ver{display:none}
  .top .menubtn{width:34px;height:34px}
  .projbar{flex-wrap:nowrap;gap:8px;padding-block:6px;overflow-x:auto;scrollbar-width:none}
  .projbar::-webkit-scrollbar{display:none}
  .projbar .label,.projbar .savest{display:none}
  .projbar select{max-width:48vw;flex:0 1 auto}
  .projbar .eps{flex-wrap:nowrap}
  .projbar .ep{padding:4px 9px;font-size:12.5px;white-space:nowrap;flex:0 0 auto}.projbar .ep i{display:none}.projbar .pver{flex:0 0 auto}
  body.hdr-hide .top,body.hdr-hide .projbar{display:none}
  .banner{padding-block:4px;font-size:12px}
  /* découpage : une carte par plan */
  .dc .dct-wrap{border:0;background:transparent;overflow:visible;margin-top:10px}
  table.dct,.dct tbody{display:block!important;width:100%!important;min-width:0!important}
  .dct thead{display:none}
  .dct tr{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);grid-template-areas:"seq seq" "thumb thumb" "plan cam" "desc desc" "audio audio" "notes notes";border:1px solid var(--line);border-radius:10px;margin:0 0 10px;overflow:hidden;background:var(--surface)}
  .dct tr.dct-add{display:block;border:0;background:transparent;margin:-2px 0 18px}
  .dct tr.dct-add td{border:0;padding:0}
  .dct td{display:block;width:auto!important;border:0!important}
  .dct tr.first td{border-top:0!important}
  .dct-seq{grid-area:seq;display:flex!important;flex-wrap:wrap;align-items:baseline;gap:4px 10px;border-right:0!important;border-bottom:1px solid var(--line)!important}
  .dct-seq b{font-size:22px}.dct-seq .h{margin-top:0;font-size:12px}.dct-seq small{margin-top:0;flex-basis:100%}.dct-seq .prog{margin-top:0}
  .dct-plan{grid-area:plan;border-right:1px solid var(--line)!important}
  .dct-cam{grid-area:cam}
  .dct-thumb{grid-area:thumb;padding:0!important}.dct-thumb .dc-frame{width:100%!important;max-width:none!important;border-radius:0}
  .dct-desc{grid-area:desc}.dct-audio{grid-area:audio}.dct-notes{grid-area:notes}
  .dct-desc,.dct-audio,.dct-notes{border-top:1px solid var(--line)!important}
  .dct td.ed::before{content:attr(data-l);display:block;padding:8px 10px 0;font-size:10.5px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:var(--muted)}
  .dct td.ed textarea{font-size:15px}
  /* cibles tactiles plus grandes */
  .dc-done input,.p-done input,.d-done input,.addsc input{width:26px;height:26px}
  .dc-done{bottom:8px;right:8px}
  .pmove,.prm{width:38px;height:38px}
  .btn.small{min-height:34px}
  .pstrip{grid-template-columns:8px 34px 30px minmax(0,1fr) auto auto auto;padding-block:8px}
  .el{padding:5px 6px 5px 9px;font-size:13.5px}
  .el button{min-width:28px;min-height:26px}
}
/* menu principal */''')

t = re.sub(r'const APP_VERSION="1\.17\.\d";', 'const APP_VERSION="1.18.0";', t)
open(p, "w", encoding="utf-8").write(t); print("ok", p)
t = open(p, encoding="utf-8").read()
R('''function goTab(t){if(S.tab===t)return;''', '''function goTab(t){document.body.classList.remove("hdr-hide");if(S.tab===t&&!S.home)return;leaveHome();''')
R('''$("#b-menu").onclick=e=>mainMenu(e.currentTarget);''', '''$("#b-menu").onclick=e=>mainMenu(e.currentTarget);
$("#b-search").onclick=()=>openSearch();
/* téléphone : l'en-tête se replie quand on fait défiler vers le bas, revient quand on remonte */
(function(){const last=new WeakMap();
  document.addEventListener("scroll",e=>{
    if(!matchMedia("(max-width:760px)").matches){document.body.classList.remove("hdr-hide");return;}
    const el=e.target===document?document.scrollingElement:e.target;if(!el||el.nodeType!==1)return;
    if(el.closest&&el.closest(".scrim,.pop,.dc-pop,.sc-drop,.cop-panel,.projbar,.tabbar"))return;
    const y=el.scrollTop;const p=last.has(el)?last.get(el):y;last.set(el,y);
    if(y-p>10&&y>90)document.body.classList.add("hdr-hide");else if(p-y>10||y<30)document.body.classList.remove("hdr-hide");},true);})();''')
open(p, "w", encoding="utf-8").write(t); print("ok2")
# icône « réglages de la page » (différente du menu principal) pour le découpage et le plan de travail
t = open(p, encoding="utf-8").read()
SL = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h9M17 7h3M4 17h3M11 17h9"/><circle cx="15" cy="7" r="2"/><circle cx="9" cy="17" r="2"/></svg>'
for bid in ['id="dc-menu"', 'id="pl-menu"']:
    i = t.index(bid); j = t.index('</button>', i)
    seg = t[i:j]; k = seg.index('<svg'); t = t[:i] + seg[:k] + SL + t[j:]
R('''Ouvre le menu ☰ puis <b>Proposer un plan</b>''', '''Ouvre les réglages de la page (icône à curseurs) puis <b>Proposer un plan</b>''')
open(p, "w", encoding="utf-8").write(t); print("ok3")
