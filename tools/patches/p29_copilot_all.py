# UpCopilot : accès à tout le projet (scénario, découpage, dépouillement, plan de travail) et actions sur chacun.
# Corrections du scénario par remplacements ciblés (aperçu avant d'appliquer) ou relecture scène par scène pour les longs scénarios.
# Annulation générique : toute l'application passe par l'historique (⌘Z marche aussi).
import re, sys
p = sys.argv[1]; t = open(p, encoding="utf-8").read()
def R(a, b, n=1):
    global t
    c = t.count(a)
    assert c == n, (a[:90], c)
    t = t.replace(a, b)
def cut(start, end):
    global t
    i = t.index(start); j = t.index(end, i)
    return i, j

# ---------- accueil du panneau ----------
R('''    intro.textContent="Bonjour ! Je peux modifier le découpage de cet épisode : redécouper une scène, raccourcir les plans pour tenir une durée, ajouter ou supprimer des plans, ou répondre à une question. Je te montre toujours ce que je propose avant de l'appliquer.";''',
  '''    intro.textContent="Bonjour ! J'ai accès à tout l'épisode : scénario, découpage, dépouillement et plan de travail. Je peux corriger ou réécrire le scénario, refaire le découpage, compléter le dépouillement, organiser les journées de tournage, ou répondre à une question. Je te montre toujours ce que je propose avant de l'appliquer.";''')
R('''    ["Redécoupe la scène "+first+" avec des plans plus courts","Fais tenir tout l'épisode en 2 min 30","Combien de plans et quelle durée par scène ?"].forEach(q=>{''',
  '''    ["Corrige les fautes d'orthographe du scénario","Redécoupe la scène "+first+" avec des plans plus courts","Fais tenir tout l'épisode en 2 min 30","Quels accessoires et costumes pour la première journée ?"].forEach(q=>{''')

# ---------- description des actions ----------
i, j = cut("function copDescribe(a,m){", "function copProjected(m){")
t = t[:i] + r'''const copQ=s=>"« "+String(s).replace(/\s+/g," ").slice(0,50)+(String(s).length>50?"…":"")+" »";
function copDescribe(a,m){
  const old=a._id?m.snapAll.find(x=>x.id===a._id):null;
  if(a.op==="texte"){const e=a.edits;return"Scène "+a.scene+" : "+e.slice(0,3).map(x=>copQ(x.de)+" → "+copQ(x.vers)).join(" · ")+(e.length>3?" (+"+(e.length-3)+" autre"+(e.length>4?"s":"")+")":"");}
  if(a.op==="reecrire_scene")return"Réécrire la scène "+a.scene+(a.entete?" ("+a.entete+")":"")+" : "+a.blocs.length+" bloc"+(a.blocs.length>1?"s":"");
  if(a.op==="relire")return"Relire "+(a.all?"tout le scénario":"les scènes "+a.scenes.join(", "))+(a.consigne?" : "+a.consigne:" (orthographe, grammaire, ponctuation)");
  if(a.op==="scene"){const ch=[];if(a.entete)ch.push("en-tête « "+a.entete+" »");if(a.synopsis!=null)ch.push("synopsis");if(a.tournee!=null)ch.push(a.tournee?"marquée tournée":"marquée non tournée");return"Scène "+a.scene+" : "+ch.join(", ");}
  if(a.op==="element_ajout")return"Dépouillement scène "+a.scene+" : ajouter « "+a.nom+" » ("+CAT[a.cat].label+")";
  if(a.op==="element_retrait")return"Dépouillement : retirer « "+a.nom+" »"+(a.scene?" de la scène "+a.scene:" de "+a._ids.length+" scène"+(a._ids.length>1?"s":""));
  if(a.op==="element_renommer")return"Dépouillement : renommer « "+a.nom+" » en « "+a.vers+" »"+(a._ids.length>1?" ("+a._ids.length+" scènes)":"");
  if(a.op==="journee")return"Plan de travail "+a.jour+" : date "+(a.date?fmtDate(a.date):"retirée");
  if(a.op==="journee_ajout")return"Plan de travail : nouvelle journée"+(a.date?" le "+fmtDate(a.date):"")+(a.scenes.length?" avec les scènes "+a.scenes.join(", "):"");
  if(a.op==="placer")return a.jour?"Plan de travail : placer les scènes "+a.scenes.join(", ")+" en "+a.jour:"Plan de travail : retirer du plan les scènes "+a.scenes.join(", ");
  if(a.op==="journee_suppr")return"Plan de travail : supprimer "+a.jour+" (ses scènes reviennent dans la liste)";
  if(a.op==="redecoupe")return"Redécouper la scène "+a.scene+(a.budget?" en visant "+fmtDur(a.budget):"")+(a.instructions?" : "+a.instructions:"");
  if(a.op==="delete")return"Supprimer le plan "+a.plan+(old&&old.action?" ("+String(old.action).slice(0,60)+(String(old.action).length>60?"…":"")+")":"");
  if(a.op==="target")return"Durée cible : "+fmtDur(a.seconds);
  if(a.op==="add")return"Ajouter un plan à la scène "+a.scene+(a.after?" après le "+a.after:"")+" : "+(SHOT_T[a.f.type]||"Plan moyen")+(a.f.dur!=null?", "+String(a.f.dur).replace(".",",")+" s":"")+(a.f.action?" — "+a.f.action.slice(0,70):"");
  if(a.op==="update"){const ch=[];const f=a.f;
    if(f.dur!=null)ch.push("durée "+String(old?.dur??"?").replace(".",",")+" s → "+String(f.dur).replace(".",",")+" s");
    if(f.type)ch.push(SHOT_T[f.type]);if(f.move)ch.push(f.move);if(f.angle)ch.push(f.angle);if(f.effect)ch.push("effet "+f.effect);
    if(f.action!=null)ch.push("action : "+f.action.slice(0,60));if(f.sound!=null)ch.push("son modifié");if(f.notes!=null)ch.push("notes modifiées");
    return"Plan "+a.plan+" : "+(ch.join(", ")||"aucun changement");}
  return a.op;
}
''' + t[j:]

# ---------- contexte et consigne ----------
i, j = cut("function copPrompt(req){", "async function copSend(text){")
t = t[:i] + r'''/* tout le projet, lisible par l'IA ; un très long scénario est abrégé (sauf les scènes citées dans la demande) */
const COP_TXT_MAX=110000;
const COP_TAG={a:"Action",c:"Personnage",p:"Didascalie",d:"Dialogue",t:"Transition",s:"Plan"};
const copRawText=s=>[s.heading,...sceneBlocks(s).map(b=>String(b.x||""))].join("\n");
function copSceneText(s,full){
  const bl=sceneBlocks(s).filter(b=>String(b.x||"").trim());
  if(!full){const x=bl.map(b=>b.x).join(" ").replace(/\s+/g," ");return"  (texte abrégé) "+x.slice(0,220)+(x.length>220?"…":"");}
  return bl.map(b=>"  ["+(COP_TAG[b.t]||"Action")+"] "+String(b.x).replace(/\n/g,"\n    ")).join("\n")||"  (scène vide)";
}
function copContext(req){
  const days=daysSorted();
  const len=S.scenes.reduce((a,s)=>a+copRawText(s).length+60,0);const abridged=len>COP_TXT_MAX;
  const asked=new Set((String(req).match(/\b[A-Z]?\d+[A-Z]*\b/gi)||[]).map(x=>x.toUpperCase()));
  const script=S.scenes.map(s=>"### Scène "+s.num+" — "+s.heading+(s.filmed?" (tournée)":"")+(s.synopsis?" · synopsis : "+String(s.synopsis).replace(/\s+/g," ").slice(0,160):"")+"\n"+copSceneText(s,!abridged||asked.has(String(s.num).toUpperCase()))).join("\n\n");
  const dep=S.scenes.map(s=>{const els=elsOf(s.id);if(!els.length)return"Scène "+s.num+" : (rien)";
    return"Scène "+s.num+" : "+CATS.filter(c=>els.some(e=>e.cat===c.id)).map(c=>c.id+" = "+els.filter(e=>e.cat===c.id).map(e=>e.name).join(", ")).join(" ; ");}).join("\n");
  const plan=days.map((d,i)=>"J"+(i+1)+(d.date?" ("+d.date+")":"")+" : "+(scenesOfDay(d.id).map(s=>s.num+(s.filmed?" ✓":"")).join(", ")||"aucune scène")).join("\n");
  const pool=S.scenes.filter(s=>!isPlanned(s)).map(s=>s.num).join(", ");
  return{abridged,script,dep,plan:(plan||"Aucune journée.")+"\nScènes non placées : "+(pool||"aucune")};
}
function copPrompt(req){
  const tgt=Number(P()?.targetSec)||0;const tot=sumDur(S.shots);
  const cut=v=>String(v||"").replace(/\s+/g," ").trim().slice(0,140);
  const lines=[];
  for(const s of S.scenes){const list=shotsOf(s.id);
    lines.push(`Scène ${s.num} · ${list.length} plans · ${Math.round(sumDur(list)*10)/10} s`);
    for(const x of list)lines.push(`  ${shotNum(x)} | ${x.type} | ${x.move} | ${x.angle} | ${x.effect||"—"} | ${isOpt(x)?"0 s (optionnel)":x.dur+" s"} | ${cut(x.action)} | ${cut(x.sound)}`);}
  const ctx=copContext(req);
  const hist=COP.msgs.slice(-7,-1).filter(m=>m.role!=="err").map(m=>(m.role==="user"?"Réalisateur : ":"UpCopilot : ")+m.text.slice(0,400)).join("\n");
  return `Tu es UpCopilot, l'assistant de préproduction de l'agence UP intégré à UP Slatebook. Tu as accès à tout l'épisode ouvert : le scénario, le découpage technique, le dépouillement et le plan de travail. Tu peux les lire et proposer des modifications sur chacun.

Projet : ${P()?.name||""} (${verTag(P())})
Durée du découpage : ${Math.round(tot*10)/10} s pour ${S.shots.length} plans. Durée cible : ${tgt?tgt+" s":"non définie"}.

=== SCÉNARIO ===${ctx.abridged?"\n(Scénario long : le texte des scènes non citées dans la demande est abrégé. Pour corriger ou relire tout le scénario, utilise l'action \"relire\".)":""}
${ctx.script}

=== DÉCOUPAGE TECHNIQUE (plan | type | mouvement | angle | effet | durée | action | son) ===
Valeurs autorisées — type : ${SHOT_TYPES.map(t=>t[0]+" ("+t[1]+")").join(", ")} ; move : ${MOVES.join(", ")} ; angle : ${ANGLES.join(", ")} ; effect : ${EFFECTS.join(", ")}.
${lines.join("\n")||"(aucun plan)"}

=== DÉPOUILLEMENT (catégories : ${CATS.map(c=>c.id+" = "+c.label).join(", ")}) ===
${ctx.dep}

=== PLAN DE TRAVAIL (✓ = scène tournée) ===
${ctx.plan}
${hist?`
Échanges précédents :
${hist}
`:""}
Demande du réalisateur : « ${req} »

Réponds uniquement avec ce JSON :
{"reply":"…","actions":[]}

Actions possibles :
Scénario
- {"op":"texte","scene":"1","edits":[{"de":"…","vers":"…"}]} : corrections ciblées dans une scène (en-tête compris). "de" est un extrait exact du texte actuel, assez long pour être sans ambiguïté (quelques mots autour de la faute) ; "vers" est le même extrait corrigé. Une action par scène, avec toutes ses corrections.
- {"op":"reecrire_scene","scene":"1","entete":"INT. LIEU - JOUR","blocs":[{"t":"a","x":"…"},{"t":"c","x":"SOA"},{"t":"d","x":"…"}]} : remplace tout le texte de la scène ; t = a (action), c (personnage), p (didascalie), d (dialogue), t (transition), s (plan) ; "entete" facultatif.
- {"op":"relire","scenes":[],"consigne":"…"} : relecture automatique scène par scène au moment d'appliquer (scenes vide = tout le scénario) ; à utiliser quand le scénario est abrégé ci-dessus ou très long.
- {"op":"scene","scene":"1","synopsis":"…","tournee":true} : ne mets que les champs à changer.
Découpage
- {"op":"redecoupe","scene":"1","budget":40,"instructions":"…"} : remplace tous les plans de la scène par un nouveau découpage fait d'après le texte ; budget en secondes (facultatif).
- {"op":"update","plan":"1.3","dur":2.5,"type":"GP","move":"…","angle":"…","effect":"…","action":"…","sound":"…","notes":"…"} : ne mets que les champs à changer.
- {"op":"delete","plan":"1.4"}
- {"op":"add","scene":"1","after":"1.3","type":"PM","move":"Fixe","angle":"Normal","effect":"—","dur":3,"action":"…","sound":"…","notes":""} : "after" facultatif.
- {"op":"target","seconds":150} : durée cible de l'épisode.
Dépouillement
- {"op":"element_ajout","scene":"1","cat":"props","nom":"…"}
- {"op":"element_retrait","scene":"1","cat":"props","nom":"…"} : sans "scene", retire l'élément de toutes les scènes.
- {"op":"element_renommer","cat":"props","nom":"…","vers":"…"} : dans toutes les scènes.
Plan de travail
- {"op":"journee_ajout","date":"2026-11-05","scenes":["3","5"]} : nouvelle journée à la fin (date et scènes facultatives).
- {"op":"placer","scenes":["3","5"],"jour":"J2"} : place les scènes à la fin de la journée ; "jour":"" les retire du plan.
- {"op":"journee","jour":"J2","date":"2026-11-05"} : change la date.
- {"op":"journee_suppr","jour":"J3"}

Règles :
- Pour une simple question, réponds dans "reply" et laisse "actions" vide.
- Corrections d'orthographe : corrige les fautes, accords, accents et la ponctuation sans changer le style, le sens ni le parler des personnages ; ne touche pas aux noms propres. Si le scénario est entier ci-dessus, utilise "texte" ; s'il est abrégé, utilise "relire".
- Pour faire tenir l'épisode dans une durée : raccourcis les durées et supprime les plans redondants plutôt que de tout refaire ; si une scène n'a pas de plans, utilise "redecoupe" avec un "budget". Ajoute une action "target".
- Les numéros de scène, de plan et de journée sont ceux ci-dessus, avant toute modification.
- Pour tout écran de téléphone, utilise le type PSE. Un plan à 0 s est optionnel.
- "reply" : une à trois phrases en français, en tutoyant, qui disent ce que tu proposes.`;
}
function copProofPrompt(s,consigne){
  return `Tu relis une scène de scénario en français.
Consigne : ${consigne||"corrige l'orthographe, la grammaire, les accords, les accents et la ponctuation, sans changer le style, le sens ni le parler des personnages ; ne touche pas aux noms propres."}

Scène ${s.num} — ${s.heading}
${copSceneText(s,true)}

Réponds uniquement avec ce JSON : {"edits":[{"de":"…","vers":"…"}]}
"de" est un extrait exact du texte (en-tête compris), assez long pour être sans ambiguïté ; "vers" est le même extrait corrigé. Liste vide si rien à corriger.`;
}
/* corrections : remplacements dans l'en-tête et les blocs de la scène */
function copEdits(s,edits){
  let heading=s.heading,n=0;const blocks=sceneBlocks(s).map(b=>({t:b.t,x:String(b.x||"")}));
  for(const e of edits){const rep=x=>{if(!x.includes(e.de))return x;n+=x.split(e.de).length-1;return x.split(e.de).join(e.vers);};
    heading=rep(heading);for(const b of blocks)b.x=rep(b.x);}
  return{heading,blocks,n};
}
function copValidEdits(s,list){
  const raw=copRawText(s);const out=[];
  for(const e of Array.isArray(list)?list:[]){const de=String(e?.de??"");const vers=String(e?.vers??"");
    if(!de.trim()||de===vers||de.length>2000||vers.length>4000||!raw.includes(de))continue;out.push({de,vers});}
  return out;
}
async function copWriteScene(sid,heading,blocks){
  const s=scene(sid);if(!s)return;
  const bl=blocks.map(b=>({t:b.t,x:b.t==="c"||b.t==="t"||b.t==="s"?String(b.x).toUpperCase():String(b.x)}));
  const patch={blocks:bl,body:bodyFromBlocks(bl),eighths:Math.max(1,Math.round(sceneLines({blocks:bl})/LINES_PER_PAGE*8)),updatedAt:Date.now(),updatedBy:S.me?.id||null};
  if(heading&&heading.trim()&&heading!==s.heading)Object.assign(patch,headingFields(heading,s));
  ED.sigs.delete(sid);
  await trk(base()+"/scenes/"+sid).update(patch);
}
''' + t[j:]

# ---------- lecture de la réponse ----------
R('''  const ref={},scn={};for(const s of S.scenes){scn[String(s.num)]=s.id;for(const x of shotsOf(s.id))ref[shotNum(x)]=x.id;}''',
  '''  await flushEditor();
  const ref={},scn={},dref={};for(const s of S.scenes){scn[String(s.num)]=s.id;scn[String(s.num).toUpperCase()]=s.id;for(const x of shotsOf(s.id))ref[shotNum(x)]=x.id;}
  daysSorted().forEach((d,i)=>{dref["J"+(i+1)]=d.id;});''')
R('''      else if(op==="target"&&Number(a.seconds)>0)acts.push({op,seconds:Math.round(Number(a.seconds))});}''',
  '''      else if(op==="target"&&Number(a.seconds)>0)acts.push({op,seconds:Math.round(Number(a.seconds))});
      else copParse(op,a,acts,scn,dref);}''')
R('''async function copSend(text){''', r'''const copScn=(scn,v)=>scn[String(v??"").trim()]||scn[String(v??"").trim().toUpperCase()]||null;
const copScenes=(scn,v)=>[...new Set((Array.isArray(v)?v:[]).map(x=>String(x).trim()).filter(x=>copScn(scn,x)))];
const copDay=(dref,v)=>dref[String(v||"").trim().toUpperCase()]||null;
function copParse(op,a,acts,scn,dref){
  const sid=copScn(scn,a.scene);const s=sid?scene(sid):null;
  const str=(v,n)=>typeof v==="string"?v.slice(0,n):null;
  if(op==="texte"&&s){const edits=copValidEdits(s,a.edits);if(edits.length)acts.push({op,scene:s.num,_sid:sid,edits});}
  else if(op==="reecrire_scene"&&s&&Array.isArray(a.blocs)){
    const blocs=a.blocs.filter(b=>b&&COP_TAG[b.t]&&typeof b.x==="string"&&b.x.trim()).slice(0,400).map(b=>({t:b.t,x:b.x.slice(0,4000)}));
    if(blocs.length)acts.push({op,scene:s.num,_sid:sid,entete:str(a.entete,200)||"",blocs});}
  else if(op==="relire"){const list=copScenes(scn,a.scenes);acts.push({op,all:!list.length,scenes:list,_sids:(list.length?list.map(n=>copScn(scn,n)):S.scenes.map(x=>x.id)),consigne:str(a.consigne,400)||""});}
  else if(op==="scene"&&s){const f={op,scene:s.num,_sid:sid};
    if(str(a.entete,200))f.entete=a.entete.slice(0,200);if(str(a.synopsis,400)!=null)f.synopsis=a.synopsis.slice(0,400);if(typeof a.tournee==="boolean")f.tournee=a.tournee;
    if(f.entete||f.synopsis!=null||f.tournee!=null)acts.push(f);}
  else if(op==="element_ajout"&&s&&CAT[a.cat]&&str(a.nom,120)&&a.nom.trim()){
    if(!elsOf(sid).some(e=>e.cat===a.cat&&norm(e.name)===norm(a.nom)))acts.push({op,scene:s.num,_sid:sid,cat:a.cat,nom:a.nom.trim().slice(0,120)});}
  else if((op==="element_retrait"||op==="element_renommer")&&str(a.nom,120)){
    if(op==="element_retrait"&&String(a.scene??"").trim()&&!sid)return;
    const k=norm(a.nom);const ids=S.elements.filter(e=>norm(e.name)===k&&(!CAT[a.cat]||e.cat===a.cat)&&(op!=="element_retrait"||!sid||e.sceneId===sid)).map(e=>e.id);
    if(!ids.length)return;
    if(op==="element_retrait")acts.push({op,scene:sid?s.num:"",nom:a.nom,_ids:ids});
    else if(str(a.vers,120)&&a.vers.trim()&&a.vers.trim()!==a.nom)acts.push({op,nom:a.nom,vers:a.vers.trim().slice(0,120),_ids:ids});}
  else if(op==="journee"&&copDay(dref,a.jour)){const d=String(a.date||"");if(!d||/^\d{4}-\d{2}-\d{2}$/.test(d))acts.push({op,jour:String(a.jour).toUpperCase(),_did:copDay(dref,a.jour),date:d});}
  else if(op==="journee_ajout"){const d=String(a.date||"");const list=copScenes(scn,a.scenes);acts.push({op,date:/^\d{4}-\d{2}-\d{2}$/.test(d)?d:"",scenes:list,_sids:list.map(n=>copScn(scn,n))});}
  else if(op==="placer"){const list=copScenes(scn,a.scenes);if(!list.length)return;const did=copDay(dref,a.jour);
    if(String(a.jour||"").trim()&&!did)return;acts.push({op,scenes:list,_sids:list.map(n=>copScn(scn,n)),jour:did?String(a.jour).toUpperCase():"",_did:did});}
  else if(op==="journee_suppr"&&copDay(dref,a.jour))acts.push({op,jour:String(a.jour).toUpperCase(),_did:copDay(dref,a.jour)});
}
async function copSend(text){''')

# ---------- application et annulation (toutes les écritures passent par l'historique) ----------
i, j = cut("async function copApply(m){", "/* ---------- export du découpage")
t = t[:i] + r'''async function copApply(m){
  const label="UpCopilot : "+String(COP.msgs[COP.msgs.indexOf(m)-1]?.text||"modification").slice(0,40);
  const prev=H.undo[H.undo.length-1];
  await hGroup(label,()=>copApplyRun(m));
  const last=H.undo[H.undo.length-1];if(m.state==="applied"&&last&&last!==prev)m.step=last;drawCop();
}
const COP_TAB=a=>["texte","reecrire_scene","relire","scene"].includes(a.op)?"script":a.op.startsWith("element")?"scenes":["journee","journee_ajout","placer","journee_suppr"].includes(a.op)?"plan":"dec";
async function copApplyRun(m){
  if(COP.busy)return;COP.busy=true;m.state="applying";COP.busyText="Application des changements…";drawCop();
  await flushEditor();const ae=document.activeElement;if(ae&&ae.closest?.("#edpage"))ae.blur();
  let fixes=0;
  try{
    /* scénario */
    for(const a of m.actions){
      if(a.op==="texte"){const s=scene(a._sid);if(!s)continue;const r=copEdits(s,copValidEdits(s,a.edits));if(r.n){fixes+=r.n;await copWriteScene(s.id,r.heading,r.blocks);}}
      else if(a.op==="reecrire_scene"&&scene(a._sid))await copWriteScene(a._sid,a.entete||scene(a._sid).heading,a.blocs);
      else if(a.op==="scene"&&scene(a._sid)){const s=scene(a._sid);const pt={};if(a.synopsis!=null)pt.synopsis=a.synopsis;if(a.tournee!=null)pt.filmed=a.tournee;
        if(a.entete&&a.entete!==s.heading)Object.assign(pt,headingFields(a.entete,s));ED.sigs.delete(s.id);
        if(Object.keys(pt).length)await trk(base()+"/scenes/"+s.id).update({...pt,updatedAt:Date.now(),updatedBy:S.me?.id||null});}
    }
    /* dépouillement */
    for(const a of m.actions){
      if(a.op==="element_ajout"&&scene(a._sid)&&!elsOf(a._sid).some(e=>e.cat===a.cat&&norm(e.name)===norm(a.nom)))
        await trk(base()+"/elements/"+uid()).set({sceneId:a._sid,cat:a.cat,name:a.nom,src:"manual",by:S.me?.id||null,at:Date.now()},{before:null});
      else if(a.op==="element_retrait")await chunked(a._ids.filter(id=>S.elements.some(e=>e.id===id)),5,id=>trk(base()+"/elements/"+id).delete());
      else if(a.op==="element_renommer")await chunked(a._ids.filter(id=>S.elements.some(e=>e.id===id)),5,id=>trk(base()+"/elements/"+id).update({name:a.vers}));
    }
    /* découpage */
    for(const a of m.actions){
      if(a.op==="update"){if(S.shots.some(x=>x.id===a._id))await shotDoc(a._id).update({...a.f,updatedAt:Date.now(),updatedBy:S.me?.id||null});}
      else if(a.op==="delete"){if(S.shots.some(x=>x.id===a._id))await shotDoc(a._id).delete();}
      else if(a.op==="target"){await trk("projects/"+S.pid).update({targetSec:a.seconds});}
    }
    for(const a of m.actions){
      if(a.op==="add"){const after=a._after?S.shots.find(x=>x.id===a._after):null;await addShot(a._sid,after,a.f);}
    }
    /* plan de travail */
    for(const a of m.actions){
      if(a.op==="journee"&&S.days.some(d=>d.id===a._did))await trk(base()+"/days/"+a._did).update({date:a.date||""});
      else if(a.op==="journee_ajout"){const max=S.days.reduce((x,d)=>Math.max(x,d.order||0),0);const id=uid();
        await trk(base()+"/days/"+id).set({order:max+1,date:a.date||"",createdAt:Date.now()},{before:null});
        if(a._sids.length){await new Promise(r=>setTimeout(r,60));await moveScenesRaw(a._sids.filter(x=>scene(x)),id,null);}}
      else if(a.op==="placer")await moveScenesRaw(a._sids.filter(x=>scene(x)),a._did&&S.days.some(d=>d.id===a._did)?a._did:null,null);
    }
    for(const a of m.actions){
      if(a.op==="journee_suppr"&&S.days.some(d=>d.id===a._did)){await chunked(scenesOfDay(a._did),5,s=>trk(base()+"/scenes/"+s.id).update({dayId:null,dayPos:null}));await trk(base()+"/days/"+a._did).delete();}
    }
    /* actions qui rappellent l'IA */
    for(const a of m.actions){
      if(a.op!=="redecoupe")continue;const s=scene(a._sid);if(!s)continue;
      COP.busyText="Redécoupage de la scène "+s.num+"…";drawCop();
      await chunked(shotsOf(a._sid),5,x=>shotDoc(x.id).delete());
      const extra=[a.instructions,a.budget?"Durée totale visée pour cette scène : environ "+a.budget+" secondes.":""].filter(Boolean).join(" ");
      await decoupeScene(a._sid,{extra});
    }
    let touched=0;
    for(const a of m.actions){
      if(a.op!=="relire")continue;const ids=a._sids.filter(x=>scene(x));
      for(let k=0;k<ids.length;k++){const s=scene(ids[k]);if(!s)continue;
        COP.busyText="Relecture de la scène "+s.num+" ("+(k+1)+"/"+ids.length+")…";drawCop();
        let res;try{res=await S.sample.json(copProofPrompt(s,a.consigne));}catch(e){if(["no_key","bad_key","no_credit","offline","rate_limited","cancelled"].includes(e?.code))throw e;continue;}
        const cur=scene(ids[k]);if(!cur)continue;const r=copEdits(cur,copValidEdits(cur,res?.edits));
        if(r.n){fixes+=r.n;touched++;await copWriteScene(cur.id,r.heading,r.blocks);}}
    }
    m.state="applied";
    if(m.actions.some(a=>a.op==="texte"||a.op==="relire"))m.note=fixes?fixes+" correction"+(fixes>1?"s":"")+" appliquée"+(fixes>1?"s":""):"Aucune correction à faire";
    const tab=COP_TAB(m.actions[0]);ED.sigs.clear();if(S.tab!==tab)goTab(tab);else render();
  }catch(e){m.state="pending";writeErr(e);}
  finally{COP.busy=false;drawCop();}
}
/* annuler : on remet chaque document touché dans son état d'avant (étape de l'historique enregistrée à l'application) */
async function copUndo(m){return hGroup("Annulation UpCopilot",()=>copUndoRun(m));}
async function copUndoRun(m){
  if(COP.busy||!m.step)return;COP.busy=true;COP.busyText="Retour à l'état d'avant…";drawCop();
  try{
    for(const o of [...m.step.ops].reverse()){
      let cur;if(o.patch){const pj=P()||{};cur={};for(const k of Object.keys(o.before||{}))cur[k]=pj[k]===undefined?null:pj[k];}else cur=hCur(o.path);
      await hApply(o.path,o.before,o.patch);hRec(o.path,cur,o.before,null,null,o.patch);}
    m.state="undone";ED.sigs.clear();render();
  }catch(e){writeErr(e);}
  finally{COP.busy=false;drawCop();}
}

''' + t[j:]
# statut « Appliqué » : nombre de corrections
R('''  else if(m.state==="applied"){const s=document.createElement("span");s.className="cop-st ok";s.textContent="Appliqué";row.append(s);btn("Annuler les changements","",()=>copUndo(m)).disabled=COP.busy;}''',
  '''  else if(m.state==="applied"){const s=document.createElement("span");s.className="cop-st ok";s.textContent="Appliqué"+(m.note?" · "+m.note:"");row.append(s);if(m.step)btn("Annuler les changements","",()=>copUndo(m)).disabled=COP.busy;}''')
# un aperçu de corrections peut être long : la liste défile
R('''.cop-acts ul{margin:0;padding-left:18px;font-size:13px;display:flex;flex-direction:column;gap:3px}''',
  '''.cop-acts ul{margin:0;padding-left:18px;font-size:13px;display:flex;flex-direction:column;gap:3px;max-height:260px;overflow:auto}''')
t = re.sub(r'const APP_VERSION="1\.22\.\d";', 'const APP_VERSION="1.23.0";', t)
open(p, "w", encoding="utf-8").write(t); print("ok", p)
