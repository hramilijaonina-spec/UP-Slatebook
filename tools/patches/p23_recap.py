# Dépouillement : vue « Récapitulatif » (tous les éléments du projet, leurs scènes, leurs journées), à côté de « Par scène ».
import re, sys
p = sys.argv[1]; t = open(p, encoding="utf-8").read()
def R(a, b, n=1):
    global t
    c = t.count(a)
    assert c == n, (a[:90], c)
    t = t.replace(a, b)

# --- état et aiguillage ---
R('''  if(S.tab==="reports"){desk.innerHTML=`<section class="reports" id="reports"></section>`;renderReports();return;}''',
  '''  if(S.tab==="reports"){S.tab="scenes";S.depView="recap";}
  if(S.tab==="scenes"&&S.depView==="recap"){if(!$("#recap"))desk.innerHTML=`<section class="reports recap" id="recap" aria-label="Récapitulatif du dépouillement"></section>`;renderRecap();return;}''')
R('''  const vis=S.tab==="reports"?"plan":S.tab;tabs.dataset.active=vis;''', '''  const vis=S.tab==="reports"?"scenes":S.tab;tabs.dataset.active=vis;''')
R('''  pane.innerHTML=`<div class="scene-head">''', '''  pane.innerHTML=`${depSwitchHTML()}<div class="scene-head">''')
# le plan de travail ouvre désormais le récapitulatif dans le dépouillement
R('''      <button class="btn" type="button" data-a="reports">Rapports</button>''', '''      <button class="btn" type="button" data-a="reports">Récapitulatif du dépouillement</button>''')
R('''  const act={reports:()=>goTab("reports"),''', '''  const act={reports:()=>openRecap(),''')
R('''on("pl-reports",()=>goTab("reports"));''', '''on("pl-reports",()=>openRecap());''')

# --- vue Récapitulatif ---
R('''function renameElement(a){''', '''/* sélecteur « Par scène | Récapitulatif » en haut du dépouillement */
S.depView=store.get("upsb.dep.view")==="recap"?"recap":"scene";
function depSwitchHTML(){return `<div class="dep-sw" role="tablist" aria-label="Affichage du dépouillement">
  <button type="button" role="tab" data-v="scene" aria-selected="${S.depView!=="recap"}">Par scène</button>
  <button type="button" role="tab" data-v="recap" aria-selected="${S.depView==="recap"}">Récapitulatif</button></div>`;}
function setDepView(v){if(S.depView===v&&S.tab==="scenes")return;S.depView=v;store.set("upsb.dep.view",v);leaveHome();S.tab="scenes";$("#desk").innerHTML="";render();}
function openRecap(){setDepView("recap");}
document.addEventListener("click",e=>{const b=e.target.closest?.(".dep-sw button[data-v]");if(b)setDepView(b.dataset.v);});
/* ouvre la scène sur les passages de l'élément */
function recapGo(sid,eid){S.depView="scene";store.set("upsb.dep.view","scene");leaveHome();S.tab="scenes";$("#desk").innerHTML="";selectScene(sid);if(eid)setTimeout(()=>findStart(eid),250);}
function recapMenu(a,anchor){
  if(!S.canWrite)return;
  openPop(anchor.getBoundingClientRect(),a.name+" · "+a.scenes.length+" scène"+(a.scenes.length>1?"s":""),[
    {label:"Renommer ou fusionner…",run:()=>renameElement(a)},
    ...CATS.filter(c=>c.id!==a.cat).map(c=>({label:"Déplacer vers "+c.label,color:c.color,run:()=>hGroup("« "+a.name+" » → "+c.label,()=>chunked(a.ids,5,id=>trk(base()+"/elements/"+id).update({cat:c.id}))).catch(writeErr)})),
    {label:"Retirer de toutes les scènes",danger:true,run:()=>hGroup("Retirer « "+a.name+" » partout",()=>chunked(a.ids,5,id=>trk(base()+"/elements/"+id).delete())).catch(writeErr)}]);
}
function renderRecap(){
  const box=$("#recap");if(!box)return;
  const q=norm(S.rpSearch);const agg=aggregate();const dix=dayIndexMap();
  const counts={};for(const a of agg)counts[a.cat]=(counts[a.cat]||0)+1;
  const rows=agg.filter(a=>(!S.filterCat||a.cat===S.filterCat)&&(!q||norm(a.name).includes(q)));
  const focus=document.activeElement?.id==="rp-search";const st=box.scrollTop;
  const bySid=a=>{const m={};for(const id of a.ids){const e=S.elements.find(x=>x.id===id);if(e&&!m[e.sceneId])m[e.sceneId]=id;}return m;};
  let body="";
  for(const c of CATS){const list=rows.filter(r=>r.cat===c.id).sort((a,b)=>b.scenes.length-a.scenes.length||a.name.localeCompare(b.name,"fr"));if(!list.length)continue;
    body+=`<section class="rc-cat" style="--c:${c.color}"><h3><i></i>${c.label}<small>${list.length}</small></h3><div class="rc-list">`;
    body+=list.map(a=>{const m=bySid(a);const days=[...new Set(a.scenes.filter(isPlanned).map(s=>dix[s.dayId]))].sort((x,y)=>x-y);
      const pages=a.scenes.reduce((x,s)=>x+(s.eighths||0),0);
      return `<div class="rc-row">
        <div class="rc-name" tabindex="0"><b>${esc(a.name)}</b>
          <span class="rc-tip" role="tooltip"><span class="label">Utilisé dans ${a.scenes.length} scène${a.scenes.length>1?"s":""}</span>${a.scenes.map(s=>`<span><b>${esc(s.num)}</b> ${esc(s.heading)}</span>`).join("")}</span></div>
        <div class="rc-sc">${a.scenes.map(s=>`<button type="button" class="scref" data-sid="${esc(s.id)}" data-eid="${esc(m[s.id]||"")}" title="${esc(s.num+" · "+s.heading)}">${esc(s.num)}</button>`).join("")}</div>
        <div class="rc-meta"><span>${a.scenes.length} sc.</span><span>${fmtE(pages)} p.</span>${days.length?`<span class="rc-days">${days.map(d=>"J"+(d+1)).join(" · ")}</span>`:""}</div>
        ${S.canWrite?`<button type="button" class="rc-more" data-key="${esc(a.key)}" aria-label="Options pour ${esc(a.name)}">⋯</button>`:""}
      </div>`;}).join("");
    body+=`</div></section>`;}
  box.innerHTML=`<div class="rp-inner">
    ${depSwitchHTML()}
    <div class="rc-head">
      <div class="stats">
        <div class="stat"><b>${agg.length}</b><span>éléments</span></div>
        <div class="stat"><b>${counts.cast||0}</b><span>rôles</span></div>
        <div class="stat"><b>${counts.props||0}</b><span>accessoires</span></div>
        <div class="stat"><b>${S.scenes.filter(s=>s.status==="ok").length}<small> / ${S.scenes.length}</small></b><span>scènes vérifiées</span></div>
      </div>
      ${S.dl?`<button type="button" class="btn" id="rc-export">Exporter…</button>`:""}
    </div>
    <div class="filters">
      <input type="search" id="rp-search" placeholder="Chercher un élément" value="${esc(S.rpSearch)}" aria-label="Chercher un élément">
      <button class="fchip" aria-pressed="${!S.filterCat}" data-cat="">Toutes</button>
      ${CATS.filter(c=>counts[c.id]).map(c=>`<button class="fchip" style="--c:${c.color}" aria-pressed="${S.filterCat===c.id}" data-cat="${c.id}"><i></i>${c.label} ${counts[c.id]}</button>`).join("")}
    </div>
    ${rows.length?body:`<p class="empty">${agg.length?"Aucun élément ne correspond.":"Aucun élément pour l'instant. Analyse les scènes avec l'IA ou ajoute les éléments à la main dans « Par scène »."}</p>`}
    <p class="hint" style="margin:0">${matchMedia("(hover:hover)").matches?"Survole un élément pour voir ses scènes. ":""}Un numéro de scène ouvre la scène sur les passages de l'élément.</p>
  </div>`;
  box.scrollTop=st;
  const rs=$("#rp-search");if(focus){rs.focus({preventScroll:true});rs.setSelectionRange(rs.value.length,rs.value.length);}
  rs.oninput=e=>{S.rpSearch=e.target.value;renderRecap();};
  box.querySelectorAll(".fchip[data-cat]").forEach(b=>b.onclick=()=>{S.filterCat=b.dataset.cat||null;renderRecap();});
  box.querySelectorAll(".scref").forEach(b=>b.onclick=()=>recapGo(b.dataset.sid,b.dataset.eid));
  box.querySelectorAll(".rc-more").forEach(b=>b.onclick=()=>{const a=agg.find(x=>x.key===b.dataset.key);if(a)recapMenu(a,b);});
  const ex=$("#rc-export");if(ex)ex.onclick=()=>openExport("dep");
}
function renameElement(a){''')

# --- renommer : propose les noms existants ; fusionne sans créer de doublon dans une scène ---
i = t.index('function renameElement(a){'); j = t.index('\n}\n', i) + 3
t = t[:i] + '''function renameElement(a){
  const same=aggregate().filter(x=>x.cat===a.cat&&x.key!==a.key).sort((x,y)=>x.name.localeCompare(y.name,"fr"));
  const m=modal(`<h3>Renommer ou fusionner</h3><p class="empty">« ${esc(a.name)} » apparaît dans ${a.scenes.length} scène${a.scenes.length>1?"s":""}. Le nouveau nom s'applique partout. Choisis un nom déjà utilisé dans ${esc(CAT[a.cat]?.label||"cette catégorie")} pour fusionner les deux.</p>
    <input type="text" id="re" value="${esc(a.name)}" list="re-list" aria-label="Nouveau nom"><datalist id="re-list">${same.map(x=>`<option value="${esc(x.name)}">`).join("")}</datalist>
    ${same.length?`<div class="re-sugg">${same.slice(0,12).map(x=>`<button type="button" class="fchip" data-n="${esc(x.name)}">${esc(x.name)} · ${x.scenes.length}</button>`).join("")}</div>`:""}
    <div class="mfoot"><button class="btn" id="re-c">Annuler</button><button class="btn primary" id="re-ok">Appliquer</button></div>`);
  const i=m.querySelector("#re");i.focus();i.select();m.querySelector("#re-c").onclick=()=>m.remove();
  m.querySelectorAll(".re-sugg [data-n]").forEach(b=>b.onclick=()=>{i.value=b.dataset.n;i.focus();});
  const go=async()=>{const v=i.value.trim();m.remove();if(!v||v===a.name)return;
    const k=norm(v);
    try{let merged=0;
      await hGroup("Renommer « "+a.name+" » en « "+v+" »",()=>chunked(a.ids,5,async id=>{const e=S.elements.find(x=>x.id===id);if(!e)return;
        const dup=S.elements.find(x=>x.id!==id&&x.sceneId===e.sceneId&&x.cat===e.cat&&norm(x.name)===k);
        if(dup){merged++;await trk(base()+"/elements/"+id).delete();}else await trk(base()+"/elements/"+id).update({name:v});}));
      toast(merged?"Fusionné avec « "+v+" ».":"Renommé dans "+a.scenes.length+" scène"+(a.scenes.length>1?"s":"")+".");}catch(e){writeErr(e);}};
  m.querySelector("#re-ok").onclick=go;i.onkeydown=e=>{if(e.key==="Enter")go();};
}
''' + t[j:]

# --- styles ---
R('''/* menu principal */''', '''/* dépouillement : Par scène | Récapitulatif */
.dep-sw{display:inline-flex;align-self:flex-start;gap:2px;padding:3px;border:1px solid var(--line);border-radius:9px;background:var(--sunk)}
.scriptpane>.dep-sw{display:flex;width:max-content;margin:0 auto 12px}
.dep-sw button{border:0;background:transparent;padding:6px 14px;border-radius:6px;font-weight:600;font-size:13px;color:var(--muted)}
.dep-sw button[aria-selected=true]{background:var(--surface);color:var(--fg);box-shadow:0 1px 3px rgb(0 0 0 / .3)}
.recap .rp-inner{gap:14px}
.rc-head{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px}
.recap .filters input{flex:1 1 220px;min-width:0;background:var(--surface);border:1px solid var(--line-strong);border-radius:var(--r);padding:7px 10px;color:var(--fg)}
.rc-cat{border:1px solid var(--line);border-radius:10px;background:var(--surface);overflow:visible}
.rc-cat h3{display:flex;align-items:center;gap:8px;margin:0;padding:10px 14px;font-family:var(--f-display);font-size:17px;letter-spacing:.03em;text-transform:uppercase;border-bottom:1px solid var(--line);background:color-mix(in srgb,var(--c) 10%,var(--surface));border-radius:10px 10px 0 0}
.rc-cat h3 i{width:11px;height:11px;border-radius:2px;background:var(--c)}
.rc-cat h3 small{font-family:var(--f-ui);font-size:12px;color:var(--muted);font-weight:600;letter-spacing:0}
.rc-row{display:grid;grid-template-columns:minmax(150px,1.1fr) minmax(0,2fr) auto 34px;gap:6px 14px;align-items:center;padding:8px 10px 8px 14px;border-bottom:1px solid var(--line)}
.rc-row:last-child{border-bottom:0}
.rc-name{position:relative;min-width:0;outline:none}
.rc-name>b{font-weight:600;font-size:14px;border-bottom:1px dotted color-mix(in srgb,var(--c) 70%,transparent);cursor:default}
.rc-tip{display:none;position:absolute;left:0;top:calc(100% + 6px);z-index:30;min-width:240px;max-width:min(420px,80vw);max-height:260px;overflow:auto;padding:8px 10px;background:var(--surface);border:1px solid var(--line-strong);border-left:3px solid var(--c);border-radius:8px;box-shadow:0 10px 28px rgb(0 0 0 / .45);flex-direction:column;gap:3px;font-size:12.5px}
.rc-tip>span:not(.label){white-space:nowrap;overflow:hidden;text-overflow:ellipsis;text-transform:uppercase;font-size:12px}
.rc-tip b{font-family:var(--f-display);font-size:14px;margin-right:4px;color:var(--c)}
@media (hover:hover){.rc-name:hover .rc-tip,.rc-name:focus .rc-tip{display:flex}}
.rc-sc{display:flex;flex-wrap:wrap;gap:3px}
.rc-sc .scref{min-width:26px;padding:2px 6px;font-size:13px}
.rc-meta{display:flex;gap:10px;font-size:12px;color:var(--muted);white-space:nowrap;font-variant-numeric:tabular-nums}
.rc-days{color:var(--ok)}
.rc-more{border:1px solid var(--line);background:transparent;border-radius:6px;width:30px;height:30px;color:var(--muted)}
.rc-more:hover{border-color:var(--accent);color:var(--fg)}
.re-sugg{display:flex;flex-wrap:wrap;gap:5px;max-height:120px;overflow:auto}
@media (max-width:760px){
  .rc-row{grid-template-columns:minmax(0,1fr) 38px;grid-template-areas:"name more" "sc sc" "meta meta"}
  .rc-name{grid-area:name}.rc-sc{grid-area:sc}.rc-meta{grid-area:meta;flex-wrap:wrap}.rc-more{grid-area:more;width:38px;height:38px}
  .rc-sc .scref{min-width:34px;min-height:30px;font-size:14px}
  .recap{padding-inline:10px}
}
/* menu principal */''')
t = re.sub(r'const APP_VERSION="1\.18\.\d";', 'const APP_VERSION="1.19.0";', t)
open(p, "w", encoding="utf-8").write(t); print("ok", p)
