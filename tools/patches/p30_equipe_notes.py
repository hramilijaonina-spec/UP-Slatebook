# Onglet « Équipe » : liste technique par département (poste, nom, contact, jours de présence, adresse, transport)
# + « Notes générales » du projet (menu Projet). Tout est annulable, enregistré dans les versions et connu de l'assistant.
import re, sys
p = sys.argv[1]; t = open(p, encoding="utf-8").read()
def R(a, b, n=1):
    global t
    c = t.count(a)
    assert c == n, (a[:90], c)
    t = t.replace(a, b)

# ---------- données : collection crew ----------
R('''days:[],locations:[],planGroup:"lieu"''', '''days:[],locations:[],crew:[],planGroup:"lieu"''')
R('''S.days=[];S.locations=[];S.sid=null;''', '''S.days=[];S.locations=[];S.crew=[];S.sid=null;''')
R('''  S.unsubP.push(S.db.collection(b+"/locations").onSnapshot(snap=>{S.locations=snap.docs.map(d=>({id:d.id,...d.data()}));render();},onErr));''',
  '''  S.unsubP.push(S.db.collection(b+"/locations").onSnapshot(snap=>{S.locations=snap.docs.map(d=>({id:d.id,...d.data()}));render();},onErr));
  S.unsubP.push(S.db.collection(b+"/crew").onSnapshot(snap=>{S.crew=snap.docs.map(d=>({id:d.id,...d.data()}));render();},onErr));''')
R('''...S.locations.map(x=>bs+"/locations/"+x.id),...S.shots.map(x=>bs+"/shots/"+x.id),''',
  '''...S.locations.map(x=>bs+"/locations/"+x.id),...S.crew.map(x=>bs+"/crew/"+x.id),...S.shots.map(x=>bs+"/shots/"+x.id),''')
R('''days:S.days,locations:S.locations,shots:S.shots};''', '''days:S.days,locations:S.locations,crew:S.crew,shots:S.shots};''')
R('''  const cols=["scenes","elements","comments","days","locations","shots"];''', '''  const cols=["scenes","elements","comments","days","locations","crew","shots"];''')
R('''col==="locations"?S.locations:col==="comments"?S.comments:null;''', '''col==="locations"?S.locations:col==="comments"?S.comments:col==="crew"?S.crew:null;''')
# versions : l'équipe est enregistrée ; une ancienne sauvegarde (sans équipe) ne la vide pas
R('''const SNAP_COLS=["scenes","elements","shots","days","locations"];''', '''const SNAP_COLS=["scenes","elements","shots","days","locations","crew"];''')
R('''  d.locations=sortById(S.locations).map(x=>({id:x.id,...strip(x)}));''', '''  d.locations=sortById(S.locations).map(x=>({id:x.id,...strip(x)}));
  d.crew=sortById(S.crew).map(x=>({id:x.id,...strip(x)}));''')
R('''  const p=P()||{};d.project={targetSec:p.targetSec||0,pagesPerDay:p.pagesPerDay||null};''',
  '''  const p=P()||{};d.project={targetSec:p.targetSec||0,pagesPerDay:p.pagesPerDay||null,notes:p.notes||""};''')
R('''    const arrs={scenes:S.scenes,elements:S.elements,shots:S.shots,days:S.days,locations:S.locations};
    const ops=[];
    for(const col of SNAP_COLS){''', '''    const arrs={scenes:S.scenes,elements:S.elements,shots:S.shots,days:S.days,locations:S.locations,crew:S.crew};
    const ops=[];
    for(const col of SNAP_COLS){if(!Array.isArray(data[col]))continue;''')
R('''if(data.project.pagesPerDay)pu.pagesPerDay=data.project.pagesPerDay;}''', '''if(data.project.pagesPerDay)pu.pagesPerDay=data.project.pagesPerDay;if("notes" in data.project)pu.notes=data.project.notes||"";}''')

# ---------- onglet ----------
R('''<span class="l">Plan de travail</span><span class="s">Plan</span></button>''',
  '''<span class="l">Plan de travail</span><span class="s">Plan</span></button>
  <button role="tab" id="tab-crew" aria-selected="false"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="9" cy="8" r="3.2"/><path d="M3 19.5c.6-3.4 3-5.3 6-5.3s5.4 1.9 6 5.3"/><circle cx="17" cy="9" r="2.5"/><path d="M16.2 14.3c2.6.1 4.3 1.8 4.8 4.7"/></svg><span class="l">Équipe</span><span class="s">Équipe</span></button>''')
R(''':root{--t-script:#3b7fd4;--t-dec:#f0a030;--t-scenes:#e0392f;--t-plan:#6fae45}''', ''':root{--t-script:#3b7fd4;--t-dec:#f0a030;--t-scenes:#e0392f;--t-plan:#6fae45;--t-crew:#9b6dd6}''')
R('''.tabbar[data-active=plan]{--tc:var(--t-plan)}''', '''.tabbar[data-active=plan]{--tc:var(--t-plan)}.tabbar[data-active=crew]{--tc:var(--t-crew)}''')
R('''#tab-plan{--c:var(--t-plan)}''', '''#tab-plan{--c:var(--t-plan)}#tab-crew{--c:var(--t-crew)}''')
R('''  ["script","dec","scenes","plan"].forEach(t=>$("#tab-"+t).setAttribute("aria-selected",String(vis===t)));''',
  '''  ["script","dec","scenes","plan","crew"].forEach(t=>$("#tab-"+t).setAttribute("aria-selected",String(vis===t)));''')
R('''  ["script","dec","scenes","plan"].forEach(tk=>{const b=$("#tab-"+tk);if(!b)return;let box=b.querySelector(".tab-peers");''',
  '''  ["script","dec","scenes","plan","crew"].forEach(tk=>{const b=$("#tab-"+tk);if(!b)return;let box=b.querySelector(".tab-peers");''')
R('''  if(!["script","dec","scenes","plan"].includes(S.tab)||S.home''', '''  if(!["script","dec","scenes","plan","crew"].includes(S.tab)||S.home''')
R('''$("#tab-plan").onclick=()=>goTab("plan");''', '''$("#tab-plan").onclick=()=>goTab("plan");
$("#tab-crew").onclick=()=>goTab("crew");''')
R('''  if(S.tab==="plan"){if(S.dragging){S.pendingRender=true;return;}''', '''  if(S.tab==="crew"){if(!$("#crew"))desk.innerHTML=`<section class="crew" id="crew" aria-label="Équipe technique"></section>`;renderCrew();return;}
  if(S.tab==="plan"){if(S.dragging){S.pendingRender=true;return;}''')

# ---------- menu : notes générales ----------
R('''  if(cp)sub.push(["-"],["versions","Historique des versions"]);''', '''  if(cp)sub.push(["notes","Notes générales"+(String(cp.notes||"").trim()?" ●":"")]);
  if(cp)sub.push(["-"],["versions","Historique des versions"]);''')
R('''      else if(k==="versions")openVersions();''', '''      else if(k==="versions")openVersions();
      else if(k==="notes")openNotes();''')

# ---------- code ----------
R('''/* lieux de tournage */
function openLieux(){''', r'''/* ---------- notes générales du projet ---------- */
function openNotes(){
  const p=P();if(!p)return;
  const m=modal(`<h3>Notes générales · ${esc(p.name||"Projet")}</h3>
    <p class="empty" style="margin:0">Pour toute l'équipe : consignes, rappels, contacts clés, infos pratiques. Enregistré automatiquement.</p>
    <textarea id="ng-t" class="ng-t" ${S.canWrite?"":"readonly"} placeholder="${S.canWrite?"Écris ici les notes du projet…":"Aucune note pour l'instant."}" aria-label="Notes générales"></textarea>
    <div class="mfoot"><span class="empty" id="ng-st" style="margin-right:auto"></span><button class="btn primary" id="ng-c">Fermer</button></div>`);
  m.querySelector(".modal").style.maxWidth="760px";
  const ta=m.querySelector("#ng-t"),st=m.querySelector("#ng-st");ta.value=p.notes||"";
  let names={};const info=async()=>{const q=P();if(!q?.notesAt){st.textContent="";return;}
    const by=q.notesBy;if(by&&!(by in names)&&S.user){try{Object.assign(names,await S.user.profiles([by]));}catch{}}
    const who=by?(names[by]?.isMe?"toi":names[by]?.name||""):"";st.textContent="Modifié "+savedAgo(q.notesAt)+(who?" par "+who:"");};
  let tm=null;
  const save=()=>{clearTimeout(tm);if(!S.canWrite)return;const v=ta.value.slice(0,20000);if(v===(P()?.notes||""))return;st.textContent="Enregistrement…";
    trk("projects/"+S.pid).update({notes:v,notesAt:Date.now(),notesBy:S.me?.id||null},{label:"Notes générales",key:"notes"}).then(info).catch(writeErr);};
  ta.oninput=()=>{clearTimeout(tm);tm=setTimeout(save,800);};ta.onblur=save;
  m.querySelector("#ng-c").onclick=()=>m.remove();
  const obs=new MutationObserver(()=>{if(!document.body.contains(m)){save();if(S.modalRefresh===refresh)S.modalRefresh=null;obs.disconnect();}});obs.observe(document.body,{childList:true});
  const refresh=()=>{if(document.activeElement!==ta){const v=P()?.notes||"";if(ta.value!==v)ta.value=v;}info();};
  S.modalRefresh=refresh;info();if(S.canWrite)setTimeout(()=>ta.focus(),30);
}

/* ---------- équipe technique ---------- */
const DEPTS=[
  {id:"real",label:"Mise en scène",posts:["Réalisateur","1er assistant réalisateur","2e assistant réalisateur","Scripte","Directeur de casting"]},
  {id:"image",label:"Image",posts:["Directeur de la photographie","Cadreur","1er assistant caméra","2e assistant caméra","DIT","Chef électricien","Électricien","Chef machiniste","Machiniste","Pilote de drone"]},
  {id:"son",label:"Son",posts:["Chef opérateur son","Perchman","Assistant son"]},
  {id:"deco",label:"Décor",posts:["Chef décorateur","Ensemblier","Accessoiriste","Constructeur","Peintre"]},
  {id:"hmc",label:"HMC · habillage, maquillage, coiffure",posts:["Chef costumière","Habilleuse","Chef maquilleuse","Maquilleuse","Coiffeuse"]},
  {id:"regie",label:"Régie",posts:["Régisseur général","Régisseur adjoint","Chauffeur","Cantine"]},
  {id:"making",label:"Making of",posts:["Photographe de plateau","Vidéaste making of"]},
  {id:"prod",label:"Production",posts:["Producteur","Directeur de production","Chargé de production","Assistant de production"]}];
const DEPT=Object.fromEntries(DEPTS.map(d=>[d.id,d]));
const CREW_STD={real:["Réalisateur","1er assistant réalisateur","Scripte"],image:["Directeur de la photographie","1er assistant caméra","Chef électricien","Chef machiniste"],son:["Chef opérateur son","Perchman"],
  deco:["Chef décorateur","Accessoiriste"],hmc:["Chef costumière","Chef maquilleuse"],regie:["Régisseur général","Chauffeur"],making:["Photographe de plateau"],prod:["Directeur de production","Chargé de production"]};
const TRANSPORTS=["Véhicule de production","Navette","Véhicule personnel","Moto","Taxi","Taxi-be","À pied"];
const CREW_F=["post","name","contact","address","transport"];
const CREW={day:"",pending:false,focus:null};
const crewOf=dep=>S.crew.filter(c=>c.dept===dep).sort((a,b)=>(a.pos||0)-(b.pos||0)||(a.createdAt||0)-(b.createdAt||0));
const crewHere=(c,did)=>!did||!!c.allDays||(Array.isArray(c.days)&&c.days.includes(did));
const crewDoc=id=>trk(base()+"/crew/"+id);
function crewDaysTxt(c){if(c.allDays)return"Tous les jours";const ds=daysSorted();return ds.map((d,i)=>(c.days||[]).includes(d.id)?"J"+(i+1):null).filter(Boolean).join(", ")||"—";}
function crewSig(){return JSON.stringify([S.pid,S.canWrite,CREW.day,S.crew.map(c=>[c.id,c.dept,c.pos,...CREW_F.map(f=>c[f]||""),!!c.allDays,c.days||[]]),daysSorted().map(d=>[d.id,d.date])]);}
function crewContactLink(v){v=String(v||"").trim();
  const em=v.match(/[^\s@]+@[^\s@]+\.[^\s@]+/);if(em)return`<a class="cr-call" href="mailto:${esc(em[0])}" title="Écrire à ${esc(em[0])}" aria-label="Écrire"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5.5" width="18" height="13" rx="2"/><path d="m3.5 7 8.5 6 8.5-6"/></svg></a>`;
  const ph=v.match(/\+?\d[\d\s.\-]{6,}\d/);if(ph)return`<a class="cr-call" href="tel:${esc(ph[0].replace(/[\s.\-]/g,""))}" title="Appeler ${esc(ph[0])}" aria-label="Appeler"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4h3.5l1.5 4-2 1.5a11 11 0 0 0 6.5 6.5l1.5-2 4 1.5V19a1.5 1.5 0 0 1-1.6 1.5A16 16 0 0 1 3.5 5.6 1.5 1.5 0 0 1 5 4z"/></svg></a>`;
  return"";}
function crewRow(c,days){
  const ro=S.canWrite?"":" readonly";const v=f=>esc(c[f]||"");
  const inp=(f,ph,extra)=>`<input type="text" id="cr-${esc(c.id)}-${f}" data-f="${f}" value="${v(f)}" placeholder="${ph}"${extra||""}${ro} aria-label="${ph}">`;
  const dis=S.canWrite?"":" disabled";
  return`<tr data-id="${esc(c.id)}">
    <td class="cr-post">${inp("post","Poste",` list="cr-p-${esc(c.dept)}"`)}</td>
    <td class="cr-name">${inp("name","Nom")}</td>
    <td><div class="cr-contact">${inp("contact","Téléphone ou e-mail",' inputmode="tel"')}${crewContactLink(c.contact)}</div></td>
    <td><div class="cr-days" role="group" aria-label="Jours de présence"><button type="button" class="cr-dd${c.allDays?" on":""}" data-d="all" aria-pressed="${!!c.allDays}"${dis}>Tous</button>${days.map((d,i)=>{const on=!!c.allDays||(c.days||[]).includes(d.id);
      return`<button type="button" class="cr-dd${on?" on":""}${c.allDays?" all":""}" data-d="${esc(d.id)}" aria-pressed="${on}" title="${esc("J"+(i+1)+(d.date?" · "+fmtDate(d.date):""))}"${dis}>J${i+1}</button>`;}).join("")}</div></td>
    <td>${inp("address","Adresse")}</td>
    <td class="cr-tr">${inp("transport","Transport",' list="cr-tr"')}</td>
    <td class="cr-act">${S.canWrite?`<button type="button" class="cr-del" title="Retirer ce poste" aria-label="Retirer ce poste"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 3h6l1 2h4v2H4V5h4l1-2zm-3 6h12l-1 12H7L6 9zm4 2v8h2v-8h-2zm4 0v8h2v-8h-2z"/></svg></button>`:""}</td></tr>`;
}
function crewHTML(){
  const days=daysSorted();const tot=S.crew.length;const here=CREW.day?S.crew.filter(c=>crewHere(c,CREW.day)).length:tot;
  const dl=`<datalist id="cr-tr">${TRANSPORTS.map(x=>`<option value="${esc(x)}">`).join("")}</datalist>`+DEPTS.map(d=>`<datalist id="cr-p-${d.id}">${d.posts.map(x=>`<option value="${esc(x)}">`).join("")}</datalist>`).join("");
  const undo=S.canWrite?`<button class="btn ghost small icbtn h-undo" type="button" aria-label="Annuler"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 14 4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 0 11H11"/></svg></button><button class="btn ghost small icbtn h-redo" type="button" aria-label="Rétablir"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m15 14 5-5-5-5"/><path d="M20 9H9.5a5.5 5.5 0 0 0 0 11H13"/></svg></button>`:"";
  return`${dl}<div class="cr-bar">
      <h2>Équipe technique</h2><span class="cr-count">${CREW.day?here+" présent"+(here>1?"s":"")+" sur "+tot:tot+" personne"+(tot>1?"s":"")}</span>
      <label class="cr-filter"><span>Présents</span><select id="cr-day"><option value="">Tous les jours</option>${days.map((d,i)=>`<option value="${esc(d.id)}"${CREW.day===d.id?" selected":""}>J${i+1}${d.date?" · "+esc(fmtDate(d.date)):""}</option>`).join("")}</select></label>
      <span class="spacer"></span>${undo}
      <button class="btn small" id="cr-copy" type="button">Copier le tableau</button><button class="btn small" id="cr-pdf" type="button">PDF</button>
    </div>
    ${days.length?"":`<p class="empty cr-hint">Les jours de présence se cochent sur les journées du plan de travail (J1, J2…). Crée d'abord les journées dans l'onglet Plan de travail, ou coche « Tous ».</p>`}
    ${DEPTS.map(d=>{const all=crewOf(d.id);const list=all.filter(c=>crewHere(c,CREW.day));
      return`<section class="cr-dept" data-dept="${d.id}"><header><b>${esc(d.label)}</b><small>${CREW.day&&list.length!==all.length?list.length+" / "+all.length:all.length}</small>
        <span class="spacer"></span>${S.canWrite&&!all.length?`<button class="btn small ghost cr-std" type="button">Postes types</button>`:""}${S.canWrite?`<button class="btn small cr-add" type="button">+ Poste</button>`:""}</header>
        ${list.length?`<div class="cr-wrap"><table class="cr-t"><colgroup><col class="c-post"><col class="c-name"><col class="c-contact"><col class="c-days"><col class="c-addr"><col class="c-tr"><col class="c-act"></colgroup>
          <thead><tr><th>Poste</th><th>Nom</th><th>Contact</th><th>Jours de présence</th><th>Adresse</th><th>Transport</th><th></th></tr></thead>
          <tbody>${list.map(c=>crewRow(c,days)).join("")}</tbody></table></div>`:`<p class="empty cr-none">${all.length?"Personne de ce département n'est présent ce jour-là.":"Aucun poste pour l'instant."}</p>`}</section>`;}).join("")}`;
}
function renderCrew(){
  const box=$("#crew");if(!box||!S.pid)return;
  const a=document.activeElement;
  if(box.childElementCount&&a&&box.contains(a)&&a.matches("input,select")){CREW.pending=true;crewSoft(box);hButtons();return;}
  const sig=crewSig();if(box.childElementCount&&box.dataset.sig===sig&&!CREW.focus){CREW.pending=false;hButtons();return;}
  box.dataset.sig=sig;CREW.pending=false;
  const desk=$("#desk"),st=desk?desk.scrollTop:0,bs=box.scrollTop,ws=window.scrollY;
  const sl=[...box.querySelectorAll(".cr-wrap")].map(w=>w.scrollLeft);
  keepFocus(()=>{box.innerHTML=crewHTML();});
  box.querySelectorAll(".cr-wrap").forEach((w,i)=>{if(sl[i])w.scrollLeft=sl[i];});
  box.scrollTop=bs;if(desk)desk.scrollTop=st;if(window.scrollY!==ws)window.scrollTo(0,ws);
  bindCrew(box);hButtons();
  if(CREW.focus){const el=document.getElementById(CREW.focus);CREW.focus=null;if(el){el.focus({preventScroll:true});el.scrollIntoView({block:"nearest"});}}
}
/* pendant la frappe : seules les autres cellules sont mises à jour (modifs des autres membres) */
function crewSoft(box){
  const a=document.activeElement;
  box.querySelectorAll("tr[data-id]").forEach(tr=>{const c=S.crew.find(x=>x.id===tr.dataset.id);if(!c)return;
    tr.querySelectorAll("input[data-f]").forEach(i=>{if(i!==a){const v=String(c[i.dataset.f]||"");if(i.value!==v)i.value=v;}});
    tr.querySelectorAll(".cr-dd").forEach(b=>{const on=b.dataset.d==="all"?!!c.allDays:(!!c.allDays||(c.days||[]).includes(b.dataset.d));b.classList.toggle("on",on);b.setAttribute("aria-pressed",String(on));});});
}
document.addEventListener("focusout",e=>{if(!CREW.pending||!e.target.closest?.("#crew"))return;
  setTimeout(()=>{const b=$("#crew"),a=document.activeElement;if(CREW.pending&&!(b&&a&&b.contains(a)&&a.matches("input,select")))renderCrew();},120);});
function bindCrew(box){
  box.querySelector("#cr-day").onchange=e=>{CREW.day=e.target.value;renderCrew();};
  box.querySelector("#cr-copy").onclick=copyCrew;box.querySelector("#cr-pdf").onclick=exportCrewPDF;
  if(!S.canWrite)return;
  box.querySelectorAll("tr[data-id] input[data-f]").forEach(i=>{
    i.onchange=()=>{const id=i.closest("tr").dataset.id;const c=S.crew.find(x=>x.id===id);if(!c)return;const f=i.dataset.f;const v=i.value.trim().slice(0,f==="address"?300:160);
      if(v===String(c[f]||""))return;crewDoc(id).update({[f]:v,updatedAt:Date.now(),updatedBy:S.me?.id||null},{label:"Équipe · "+({post:"poste",name:"nom",contact:"contact",address:"adresse",transport:"transport"})[f]+(c.name?" de "+c.name:"")}).catch(writeErr);};
    i.onkeydown=e=>{if(e.key==="Enter"){e.preventDefault();i.blur();}};});
  box.querySelectorAll(".cr-dd").forEach(b=>b.onclick=()=>{
    const id=b.closest("tr").dataset.id;const c=S.crew.find(x=>x.id===id);if(!c)return;const ids=daysSorted().map(d=>d.id);let patch;
    if(b.dataset.d==="all")patch={allDays:!c.allDays,days:c.allDays?[]:(c.days||[])};
    else if(c.allDays)patch={allDays:false,days:ids.filter(x=>x!==b.dataset.d)};
    else{const cur=new Set((c.days||[]).filter(x=>ids.includes(x)));cur.has(b.dataset.d)?cur.delete(b.dataset.d):cur.add(b.dataset.d);patch={days:ids.filter(x=>cur.has(x)),allDays:false};
      if(ids.length&&patch.days.length===ids.length)patch={allDays:true,days:[]};}
    crewDoc(id).update({...patch,updatedAt:Date.now()},{label:"Jours de présence"+(c.name?" de "+c.name:"")}).catch(writeErr);});
  box.querySelectorAll(".cr-del").forEach(b=>b.onclick=()=>{const id=b.closest("tr").dataset.id;const c=S.crew.find(x=>x.id===id);
    crewDoc(id).delete({label:"Retirer "+(c?.name||c?.post||"un poste")}).then(()=>toast("Poste retiré. ⌘Z pour l'annuler.")).catch(writeErr);});
  box.querySelectorAll(".cr-add").forEach(b=>b.onclick=async()=>{const dep=b.closest(".cr-dept").dataset.dept;const all=crewOf(dep);const id=uid();
    CREW.focus="cr-"+id+"-post";
    try{await crewDoc(id).set({dept:dep,post:"",name:"",contact:"",address:"",transport:"",allDays:false,days:CREW.day?[CREW.day]:[],pos:(all.length?(all[all.length-1].pos||0):0)+1024,createdAt:Date.now(),createdBy:S.me?.id||null},{before:null,label:"Poste ajouté · "+DEPT[dep].label});}
    catch(e){CREW.focus=null;writeErr(e);}});
  box.querySelectorAll(".cr-std").forEach(b=>b.onclick=()=>{const dep=b.closest(".cr-dept").dataset.dept;
    hGroup("Postes types · "+DEPT[dep].label,()=>chunked(CREW_STD[dep].map((post,i)=>({post,i})),5,({post,i})=>crewDoc(uid()).set({dept:dep,post,name:"",contact:"",address:"",transport:"",allDays:false,days:[],pos:(i+1)*1024,createdAt:Date.now(),createdBy:S.me?.id||null},{before:null}))).catch(writeErr);});
}
function crewRows(){
  const out=[["Département","Poste","Nom","Contact","Jours de présence","Adresse","Transport"]];
  for(const d of DEPTS)for(const c of crewOf(d.id).filter(c=>crewHere(c,CREW.day)))out.push([d.label,c.post||"",c.name||"",c.contact||"",crewDaysTxt(c),c.address||"",c.transport||""]);
  return out;
}
function copyCrew(){
  const tsv=crewRows().map(r=>r.map(x=>String(x).replace(/[\t\n]/g," ")).join("\t")).join("\n");
  const ok=()=>toast("Liste technique copiée : colle-la dans Sheets ou Excel.");
  const fb=()=>{const ta=document.createElement("textarea");ta.value=tsv;ta.style.cssText="position:fixed;opacity:0;top:0;left:0";document.body.append(ta);ta.select();let r=false;try{r=document.execCommand("copy");}catch{}ta.remove();r?ok():toast("La copie a été refusée par le navigateur.");};
  try{navigator.clipboard.writeText(tsv).then(ok,fb);}catch{fb();}
}
async function exportCrewPDF(){
  if(!S.dl){toast("L'export n'est pas disponible ici.");return;}
  try{await loadLib("jspdf");await loadLib("autotable");}catch{toast("Impossible de charger l'outil PDF. Vérifie la connexion internet.",5000);return;}
  const{jsPDF}=window.jspdf;const doc=new jsPDF({orientation:"landscape",unit:"mm",format:"a4"});
  const days=daysSorted();const di=days.findIndex(d=>d.id===CREW.day);
  const sub=(di>-1?"Présents le J"+(di+1)+(days[di].date?" · "+fmtDate(days[di].date):""):"Toute l'équipe")+" · "+new Date().toLocaleDateString("fr-FR",{day:"numeric",month:"long",year:"numeric"});
  const body=[];
  for(const d of DEPTS){const list=crewOf(d.id).filter(c=>crewHere(c,CREW.day));if(!list.length)continue;
    body.push([{content:d.label.toUpperCase()+" · "+list.length,colSpan:6,styles:{fontStyle:"bold",fillColor:[236,230,247],textColor:[60,30,110]}}]);
    for(const c of list)body.push([c.post||"",c.name||"",c.contact||"",crewDaysTxt(c),c.address||"",c.transport||""]);}
  if(!body.length){toast("Personne dans la liste pour ce choix.");return;}
  doc.autoTable({head:[["Poste","Nom","Contact","Jours de présence","Adresse","Transport"]],body,startY:21,margin:{left:10,right:10,top:21,bottom:13},theme:"grid",
    styles:{font:"helvetica",fontSize:9,cellPadding:2,valign:"middle",lineColor:[210,210,210],lineWidth:0.2,textColor:[25,25,25],overflow:"linebreak"},
    headStyles:{fillColor:[155,109,214],textColor:[255,255,255],fontStyle:"bold"},
    columnStyles:{0:{cellWidth:46},1:{cellWidth:44,fontStyle:"bold"},2:{cellWidth:44},3:{cellWidth:40},4:{cellWidth:"auto"},5:{cellWidth:34}},
    didDrawPage:()=>{doc.setFont("helvetica","bold");doc.setFontSize(13);doc.setTextColor(25,25,25);doc.text("Liste technique · "+(P()?.name||"")+" · "+verTag(P()),10,11);
      doc.setFont("helvetica","normal");doc.setFontSize(8.5);doc.setTextColor(110,110,110);doc.text(sub,10,16.5);}});
  const n=doc.getNumberOfPages();
  for(let i=1;i<=n;i++){doc.setPage(i);doc.setFontSize(8);doc.setTextColor(130,130,130);doc.text("UP Slatebook · page "+i+" / "+n,287,203,{align:"right"});}
  await save(fileBase(P())+"-liste-technique"+(di>-1?"-J"+(di+1):"")+".pdf",doc.output("blob"));
}

/* lieux de tournage */
function openLieux(){''')

# ---------- l'assistant connaît les notes et l'équipe ----------
R('''  return{abridged,script,dep,plan:(plan||"Aucune journée.")+"\\nScènes non placées : "+(pool||"aucune")};''',
  '''  const crew=DEPTS.map(d=>{const l=crewOf(d.id);return l.length?d.label+" : "+l.map(c=>(c.post||"?")+" – "+(c.name||"à trouver")+" ("+crewDaysTxt(c)+(c.transport?", "+c.transport:"")+")").join(" ; "):null;}).filter(Boolean).join("\\n");
  return{abridged,script,dep,crew:crew||"Aucune personne dans la liste.",notes:String(P()?.notes||"").trim().slice(0,6000)||"(aucune)",plan:(plan||"Aucune journée.")+"\\nScènes non placées : "+(pool||"aucune")};''')
R('''=== PLAN DE TRAVAIL (✓ = scène tournée) ===
${ctx.plan}''', '''=== PLAN DE TRAVAIL (✓ = scène tournée) ===
${ctx.plan}

=== ÉQUIPE TECHNIQUE (lecture seule) ===
${ctx.crew}

=== NOTES GÉNÉRALES DU PROJET (lecture seule) ===
${ctx.notes}''')

# ---------- styles ----------
R('''/* présence des membres */''', '''/* équipe technique */
.crew{grid-column:1/-1;min-height:0;overflow:auto;display:flex;flex-direction:column;gap:14px;padding:16px max(16px,env(safe-area-inset-right,0px)) 80px max(16px,env(safe-area-inset-left,0px));box-sizing:border-box}
.cr-bar{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px}
.cr-bar h2{margin:0;font-family:var(--f-display);font-size:22px;letter-spacing:.03em;text-transform:uppercase}
.cr-count{color:var(--muted);font-size:13px}
.cr-filter{display:inline-flex;align-items:center;gap:6px;font-size:13px;color:var(--muted)}
.cr-filter select{background:var(--surface);color:var(--fg);border:1px solid var(--line-strong);border-radius:8px;padding:5px 8px;font:inherit;font-size:13px}
.cr-hint{margin:0}
.cr-dept{flex:0 0 auto;border:1px solid var(--line);border-radius:var(--r);background:var(--surface);overflow:hidden}
.crew>*{flex-shrink:0}
.cr-dept>header{display:flex;align-items:center;gap:8px;padding:8px 10px 8px 14px;background:var(--sunk);border-bottom:1px solid var(--line);box-shadow:inset 4px 0 0 var(--t-crew)}
.cr-dept>header b{font-size:13.5px;letter-spacing:.06em;text-transform:uppercase}
.cr-dept>header small{color:var(--muted);font-size:12px;font-weight:700;background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:0 7px}
.cr-none{margin:0;padding:10px 14px}
.cr-wrap{overflow-x:auto}
table.cr-t{width:100%;min-width:1000px;border-collapse:collapse;table-layout:fixed}
.cr-t col.c-post{width:17%}.cr-t col.c-name{width:15%}.cr-t col.c-contact{width:15%}.cr-t col.c-days{width:19%}.cr-t col.c-addr{width:19%}.cr-t col.c-tr{width:12%}.cr-t col.c-act{width:40px}
.cr-t th{text-align:left;font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);padding:7px 8px 5px}
.cr-t td{border-top:1px solid var(--line);padding:3px 4px;vertical-align:middle}
.cr-t input{width:100%;box-sizing:border-box;background:transparent;border:1px solid transparent;border-radius:6px;padding:6px 7px;color:var(--fg);font:inherit;font-size:13.5px;min-width:0}
.cr-t input:hover:not([readonly]){border-color:var(--line)}
.cr-t input:focus{outline:none;border-color:var(--t-crew);background:var(--bg)}
.cr-t input::placeholder{color:color-mix(in srgb,var(--muted) 60%,transparent)}
.cr-t td.cr-name input{font-weight:700}
.cr-contact{display:flex;align-items:center;gap:2px}
.cr-call{display:inline-grid;place-items:center;width:28px;height:28px;flex:0 0 auto;border-radius:6px;color:var(--t-crew)}
.cr-call:hover{background:var(--sunk)}
.cr-call svg,.cr-del svg{width:16px;height:16px}
.cr-call svg{fill:none;stroke:currentColor;stroke-width:1.8;stroke-linejoin:round}
.cr-days{display:flex;flex-wrap:wrap;gap:3px;padding:2px 3px}
.cr-dd{border:1px solid var(--line-strong);background:transparent;color:var(--muted);border-radius:10px;padding:2px 8px;font:inherit;font-size:11.5px;font-weight:700;cursor:pointer;line-height:1.5}
.cr-dd.on{background:var(--t-crew);border-color:var(--t-crew);color:#fff}
.cr-dd.on.all{background:color-mix(in srgb,var(--t-crew) 55%,transparent)}
.cr-dd:disabled{cursor:default}
.cr-del{display:inline-grid;place-items:center;width:30px;height:30px;border:0;background:transparent;color:var(--muted);border-radius:6px;cursor:pointer}
.cr-del svg{fill:currentColor}
.cr-del:hover{color:var(--danger);background:var(--sunk)}
.ng-t{width:100%;box-sizing:border-box;min-height:min(55vh,460px);resize:vertical;background:var(--surface);color:var(--fg);border:1px solid var(--line-strong);border-radius:var(--r);padding:12px 14px;font:inherit;font-size:14.5px;line-height:1.55}
.ng-t:focus{outline:none;border-color:var(--accent)}
@media print{.crew .cr-bar .btn,.cr-del,.cr-std,.cr-add{display:none!important}}
/* présence des membres */''')

# téléphone : cinq onglets tiennent sur la largeur
R('''<span class="s">Découpage</span>''', '''<span class="s">Découp.</span>''')
R('''/* présence des membres */''', '''@media (max-width:520px){.tabbar{gap:2px;padding-left:6px;padding-right:6px}.tabbar button{font-size:11.5px;letter-spacing:0;padding-left:2px;padding-right:2px}}
/* présence des membres */''')
t = re.sub(r'const APP_VERSION="1\.23\.\d";', 'const APP_VERSION="1.24.0";', t)
open(p, "w", encoding="utf-8").write(t); print("ok", p)
