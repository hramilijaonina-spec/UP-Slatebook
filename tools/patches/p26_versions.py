# Historique des versions : les anciennes versions (v1…) ne disparaissent plus sous les sauvegardes automatiques.
# - « Nouvelle version » enregistre d'abord la version finale de la version en cours (gardée pour toujours)
# - le tri des sauvegardes automatiques garde toujours la première et la dernière de chaque version, et une par jour au-delà des 40 récentes
# - la liste est rangée par version (v3, v2, v1…), repliable ; la fin d'une ancienne version se retrouve même pour les projets d'avant
import re, sys
p = sys.argv[1]; t = open(p, encoding="utf-8").read()
def R(a, b, n=1):
    global t
    c = t.count(a)
    assert c == n, (a[:90], c)
    t = t.replace(a, b)

# 1. passer à la version suivante : la version finale de l'actuelle est enregistrée d'abord
R('''    const list=all?sib:[p];
    try{await chunked(list,4,x=>{''', '''    const list=all?sib:[p];const v0=projVer(p);
    try{await takeSnapshot({force:true,strict:true,named:true,final:true,n:v0,label:"Version finale de la v"+v0});}catch(e){b.disabled=false;writeErr(e);return;}
    try{await chunked(list,4,x=>{''')
R('''      m.remove();try{await takeSnapshot({force:true,named:true,n,note:txt,label:"v"+n});}catch{}''',
  '''      m.remove();try{await takeSnapshot({force:true,named:true,n,note:txt,label:"Début de la v"+n});}catch{}''')
R('''    const meta={at:Date.now(),by:S.me?.id||null,hash,hv:2,parts:parts.length,size:json.length,named:!!o.named,label:o.label||"",note:o.note||"",n:o.n||projVer(P()),''',
  '''    const meta={at:Date.now(),by:S.me?.id||null,hash,hv:2,parts:parts.length,size:json.length,named:!!o.named,final:!!o.final,label:o.label||"",note:o.note||"",n:o.n||projVer(P()),''')

# 2. tri des sauvegardes automatiques
R('''async function snapPrune(keepId){
  const autos=snapsSorted().filter(s=>!s.named&&s.id!==keepId);
  const extra=autos.slice(SNAP.KEEP-1);''', '''async function snapPrune(keepId){
  const all=snapsSorted();const keep=new Set([keepId]);
  /* la première et la dernière sauvegarde de chaque version restent toujours */
  const byN=new Map();for(const s of all){const n=s.n||1;if(!byN.has(n))byN.set(n,[]);byN.get(n).push(s);}
  for(const l of byN.values()){keep.add(l[0].id);keep.add(l[l.length-1].id);}
  const autos=all.filter(s=>!s.named&&!keep.has(s.id));
  autos.slice(0,SNAP.KEEP-1).forEach(s=>keep.add(s.id));
  /* au-delà des plus récentes : une par jour pendant 60 jours */
  const days=new Set(),lim=Date.now()-60*864e5;
  for(const s of autos.slice(SNAP.KEEP-1)){const d=(s.n||1)+"|"+new Date(s.at).toDateString();if(s.at>lim&&!days.has(d)){days.add(d);keep.add(s.id);}}
  const extra=autos.filter(s=>!keep.has(s.id));''')

# 3. titres
R('''function snapTitle(s){return s.named?(s.label&&s.label!=="v"+s.n?s.label:"Nouvelle version"):(s.label||"Sauvegarde automatique");}''',
  '''function snapTitle(s){return s.named?(s.label&&s.label!=="v"+s.n?s.label:"Début de la v"+(s.n||1)):(s.label||"Sauvegarde automatique");}
const fmtDay=t=>new Date(t).toLocaleDateString("fr-FR",{day:"numeric",month:"short"});''')

# 4. revenir à une version avec un autre numéro (fin d'une ancienne version retrouvée dans le début de la suivante)
R('''async function restoreSnapshot(meta){''', '''async function restoreSnapshot(meta,o={}){const vn=o.n||meta.n||1;''')
R('''    await takeSnapshot({strict:true,label:"État avant le retour à la v"+(meta.n||1)});''',
  '''    await takeSnapshot({strict:true,label:"État avant le retour à la v"+vn});''')
R('''    const pu={version:meta.n||1};''', '''    const pu={version:vn};''')
R('''    toast("Projet revenu à la "+snapLabel(meta)+". L'état d'avant reste dans la liste des versions.",6000);''',
  '''    toast("Projet revenu à la v"+vn+" du "+fmtWhen(meta.at)+". L'état d'avant reste dans la liste des versions.",6000);''')

# 5. liste rangée par version
R('''    <p class="empty">Chaque modification est enregistrée automatiquement. Choisis une version pour que le projet revienne à cet état ; l'état actuel reste dans la liste, tu peux donc toujours y retourner.</p>''',
  '''    <p class="empty">Chaque modification est enregistrée automatiquement, rangée par version. Ouvre une version (v1, v2…) pour voir ses sauvegardes et revenir à l'une d'elles ; l'état actuel reste dans la liste, tu peux donc toujours y retourner.</p>''')
old_start = t.index("  let ps={};\n  const row=(s,cur)=>{")
old_end = t.index("    list.forEach(s=>box.append(row(s,s===cur)));\n  };\n") + len("    list.forEach(s=>box.append(row(s,s===cur)));\n  };\n")
t = t[:old_start] + '''  let ps={};const openN=new Set([projVer(p)]);let first=true;
  const row=(s,cur,o={})=>{const vn=o.n||s.n||1;const ttl=o.title||snapTitle(s);
    const d=document.createElement("div");d.className="vrow"+(s.named||o.virt?" named":"")+(cur?" cur":"");
    const b=document.createElement("b");b.textContent="v"+vn;
    const r=document.createElement("span");
    const tl=document.createElement("strong");tl.textContent=ttl;
    if(cur){const pill=document.createElement("em");pill.className="vcur";pill.textContent="Version actuelle";tl.append(pill);}
    const sm=document.createElement("small");const who=s.by?((ps[s.by]&&(ps[s.by].isMe?"toi":ps[s.by].name))||"quelqu'un"):"";
    const c=s.counts||{};sm.textContent=fmtWhen(s.at)+(who?" · "+who:"")+" · "+(c.scenes||0)+" scènes · "+(c.shots||0)+" plans · "+(c.elements||0)+" éléments";
    r.append(tl,sm);const nt=o.virt?"Identique au début de la v"+(vn+1)+".":s.note;if(nt){const pp=document.createElement("p");pp.textContent=nt;r.append(pp);}
    d.append(b,r);
    if(S.canWrite&&!cur){const act=document.createElement("span");act.className="vact";
      const go=document.createElement("button");go.className="btn small";go.type="button";go.textContent="Revenir à cette version";
      go.onclick=()=>{const c2=modal(`<h3>Revenir à la v${vn} ?</h3><p>Le projet reprend son état du <b>${esc(fmtWhen(s.at))}</b> (${esc(ttl)}) : scénario, découpage, dépouillement et plan de travail, pour toute l'équipe. Il repasse en <b>v${vn}</b>.</p><p class="empty">L'état actuel reste dans la liste des versions : tu pourras y retourner.</p><div class="mfoot"><button class="btn" id="rv-c">Annuler</button><button class="btn primary" id="rv-ok">Revenir à la v${vn}</button></div>`);
        c2.querySelector("#rv-c").onclick=()=>c2.remove();c2.querySelector("#rv-ok").onclick=()=>{c2.remove();S.modalRefresh=null;m.remove();restoreSnapshot(s,{n:vn});};};
      act.append(go);
      if(!o.virt){const del=document.createElement("button");del.className="btn small vdel";del.type="button";del.title="Supprimer cette sauvegarde";del.setAttribute("aria-label","Supprimer la v"+vn+" du "+fmtWhen(s.at));
        del.innerHTML=`<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 3h6l1 2h4v2H4V5h4l1-2zm-3 6h12l-1 12H7L6 9zm4 2v8h2v-8h-2zm4 0v8h2v-8h-2z"/></svg>`;
        del.onclick=()=>confirmSnapDelete(s);act.append(del);}
      d.append(act);}
    return d;};
  const draw=async()=>{const box=m.querySelector("#vl");if(!box)return;
    const list=snapsSorted();
    const ids=[...new Set(list.map(h=>h.by).filter(Boolean))].filter(i=>!(i in ps));
    if(S.user&&ids.length){try{Object.assign(ps,await S.user.profiles(ids));}catch{}}
    const st=box.scrollTop;box.innerHTML="";
    if(!list.length){box.innerHTML=`<p class="empty" style="padding:10px">Aucune sauvegarde pour l'instant : la première est créée quelques secondes après la prochaine modification.</p>`;return;}
    const cur=snapCurrent(curHash());const pv=projVer(P());
    if(first){first=false;if(cur)openN.add(cur.n||1);}
    /* sauvegardes rangées par numéro de version */
    const groups=new Map();for(const s of list){const n=s.n||1;if(!groups.has(n))groups.set(n,[]);groups.get(n).push(s);}
    if(!groups.has(pv))groups.set(pv,[]);
    /* projets d'avant : la fin d'une version est le « début » enregistré de la suivante */
    for(const[n2,l]of[...groups]){if(n2<2)continue;const stt=l.filter(s=>s.named&&!s.final&&(s.label==="v"+n2||s.label==="Début de la v"+n2)).pop();
      if(!stt)continue;const prev=groups.get(n2-1);if(prev&&prev.some(s=>s.final))continue;
      if(!prev)groups.set(n2-1,[]);groups.get(n2-1).virt=stt;}
    const vh=Array.isArray(P()?.versions)?P().versions:Object.values(P()?.versions||{});
    for(const n of[...groups.keys()].sort((a,b)=>b-a)){const l=groups.get(n);const open=openN.has(n);
      const cnt=l.length+(l.virt?1:0);const all=[...(l.virt?[l.virt]:[]),...l];
      const span=all.length?(all.length>1?"du "+fmtDay(all[all.length-1].at)+" au "+fmtDay(all[0].at):"le "+fmtDay(all[0].at)):"";
      const note=(vh.find(v=>Number(v?.n)===n)||{}).note||"";
      const h=document.createElement("button");h.type="button";h.className="vgrp";h.setAttribute("aria-expanded",String(open));
      h.innerHTML=`<svg class="chev" viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg><b>v${n}</b><span><strong>${n===pv?"Version en cours":"Version "+n}</strong><small>${cnt?cnt+" sauvegarde"+(cnt>1?"s":"")+(span?" · "+esc(span):""):"Pas encore de sauvegarde"}</small>${note?`<small class="vnote">${esc(note)}</small>`:""}</span>`;
      h.onclick=()=>{if(openN.has(n))openN.delete(n);else openN.add(n);draw();};
      box.append(h);
      if(!open)continue;
      if(n===pv&&!cur){const d=document.createElement("div");d.className="vrow cur";
        d.innerHTML=`<b>${esc(verTag(P()))}</b><span><strong>Modifications en cours<em class="vcur">Version actuelle</em></strong><small>${SNAP.busy||SNAP.mig?"Enregistrement…":"Enregistrées automatiquement dans quelques secondes"}</small></span>`;box.append(d);}
      if(l.virt)box.append(row(l.virt,false,{n,virt:true,title:"Version finale de la v"+n}));
      l.forEach(s=>box.append(row(s,s===cur)));
      if(!cnt&&!(n===pv&&!cur)){const e=document.createElement("p");e.className="empty";e.style.cssText="padding:8px 12px;margin:0";e.textContent="Aucune sauvegarde dans cette version.";box.append(e);}
    }
    box.scrollTop=st;
  };
''' + t[old_end:]

# 6. styles
R('''.vlist{display:flex;flex-direction:column;border:1px solid var(--line);border-radius:var(--r);max-height:280px;overflow:auto}
.vlist div{''', '''.vlist{display:flex;flex-direction:column;border:1px solid var(--line);border-radius:var(--r);max-height:min(62vh,520px);overflow:auto}
.vlist .vgrp{display:grid;grid-template-columns:16px 40px minmax(0,1fr);align-items:center;gap:2px 8px;width:100%;padding:9px 10px;border:0;border-bottom:1px solid var(--line);background:var(--sunk);color:var(--fg);text-align:left;cursor:pointer;font:inherit;position:sticky;top:0;z-index:1}
.vlist .vgrp:hover{background:color-mix(in srgb,var(--sunk) 80%,var(--accent) 8%)}
.vlist .vgrp .chev{width:14px;height:14px;fill:none;stroke:currentColor;stroke-width:2.2;transition:transform .15s}
.vlist .vgrp[aria-expanded="true"] .chev{transform:rotate(90deg)}
.vlist .vgrp small.vnote{color:var(--fg);opacity:.8;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.vlist div{''')
R('''@media (max-width:560px){.vlist div{grid-template-columns:40px minmax(0,1fr)}.vlist .vact{grid-column:2;justify-self:start}}''',
  '''@media (max-width:560px){.vlist div{grid-template-columns:40px minmax(0,1fr)}.vlist .vact{grid-column:2;justify-self:start}}
.vlist div.vrow{padding-left:22px}''')
t = re.sub(r'const APP_VERSION="1\.20\.\d";', 'const APP_VERSION="1.21.0";', t)
open(p, "w", encoding="utf-8").write(t); print("ok", p)
