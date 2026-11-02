# Dépouillement : relancer l'IA après une modification du scénario met les éléments à jour (au lieu de seulement en ajouter).
import re, sys
p = sys.argv[1]; t = open(p, encoding="utf-8").read()
def R(a, b, n=1):
    global t
    c = t.count(a)
    assert c == n, (a[:90], c)
    t = t.replace(a, b)

# empreinte du texte analysé, pour savoir si le scénario a changé depuis
R('''async function analyzeScene(sid,opts={}){''', '''const sceneTextHash=s=>snapHash(String(bodyFromBlocks(sceneBlocks(s))||s.body||"").replace(/\\s+/g," ").trim());
const textChanged=s=>!!(s&&s.analyzedHash&&s.analyzedHash!==sceneTextHash(s));
const needsAnalysis=s=>!s.status||s.status==="todo"||textChanged(s);
/* « Relancer l'IA » sur une scène déjà dépouillée : choisir ce qu'on garde */
function confirmReanalyse(sid){
  const s=scene(sid);if(!s)return;const els=elsOf(sid);
  if(!els.length){analyzeScene(sid);return;}
  const man=els.filter(e=>e.src==="manual").length,ai=els.length-man;
  const m=modal(`<h3>Relancer l'IA sur la scène ${esc(s.num)}</h3>
    ${textChanged(s)?`<p class="st ai" style="align-self:flex-start">Le texte a changé depuis la dernière analyse</p>`:""}
    <label class="ap-opt"><input type="radio" name="ra" value="update" checked><span><b>Mettre à jour</b> : l'IA relit le texte actuel. Les éléments qu'elle avait proposés et qui ne sont plus dans la scène sont retirés, les nouveaux sont ajoutés.${man?(man>1?` Tes ${man} ajouts à la main sont gardés.`:" Ton ajout à la main est gardé."):""}</span></label>
    <label class="ap-opt"><input type="radio" name="ra" value="reset"><span><b>Tout refaire</b> : les ${els.length} élément${els.length>1?"s":""} de la scène ${els.length>1?"sont effacés":"est effacé"}${man?", y compris les ajouts à la main,":""} puis l'IA refait le dépouillement.</span></label>
    <p class="empty" style="margin:0">Tu peux annuler le résultat avec ⌘Z ou le bouton ↶.</p>
    <div class="mfoot"><button class="btn" id="ra-c">Annuler</button><button class="btn primary" id="ra-ok">Relancer l'IA</button></div>`);
  m.querySelector("#ra-c").onclick=()=>m.remove();
  m.querySelector("#ra-ok").onclick=()=>{const mode=m.querySelector('input[name="ra"]:checked')?.value||"update";m.remove();analyzeScene(sid,{mode});};
}
async function analyzeScene(sid,opts={}){''')
R('''  if(opts.bulk){try{const f=await ref.get();if(f.exists&&f.data().status&&f.data().status!=="todo")return"skip";}catch{}}''',
  '''  if(opts.bulk){try{const f=await ref.get();if(f.exists){const d={...f.data(),id:sid};if(!needsAnalysis(d))return"skip";}}catch{}}''')
R('''    const items=Array.isArray(res?.elements)?res.elements:[];
    const have=new Set(elsOf(sid).map(e=>e.cat+"|"+norm(e.name)));const fresh=[];
    for(const it of items){const cat=String(it?.cat||"");const name=String(it?.name||"").trim();
      if(!CAT[cat]||!name||name.length>120)continue;const k=cat+"|"+norm(name);if(have.has(k))continue;have.add(k);fresh.push({cat,name});}
    await chunked(fresh,5,f=>S.db.collection(base()+"/elements").add({sceneId:sid,cat:f.cat,name:f.name,src:"ai",by:S.me?.id||null,at:Date.now()}));
    const cur=scene(sid)||s;const patch={status:cur.status==="ok"?"ok":"ai",analyzedAt:Date.now()};
    if(!cur.synopsis&&typeof res?.synopsis==="string")patch.synopsis=res.synopsis.slice(0,400);
    await updateScene(sid,patch);
    return"done";''', '''    const items=Array.isArray(res?.elements)?res.elements:[];
    /* ce que l'IA voit dans le texte actuel */
    const found=new Map();
    for(const it of items){const cat=String(it?.cat||"");const name=String(it?.name||"").trim();
      if(!CAT[cat]||!name||name.length>120)continue;const k=cat+"|"+norm(name);if(!found.has(k))found.set(k,{cat,name});}
    const mode=opts.mode||"update";const keyOf=e=>e.cat+"|"+norm(e.name);
    const cur0=elsOf(sid);
    /* on retire ce que l'IA avait proposé et qui n'est plus dans la scène (ou tout, en « tout refaire ») ; les ajouts à la main restent */
    const drop=mode==="reset"?cur0:cur0.filter(e=>e.src!=="manual"&&!found.has(keyOf(e)));
    const keep=new Set(cur0.filter(e=>!drop.includes(e)).map(keyOf));
    const add=[...found.entries()].filter(([k])=>!keep.has(k)).map(([,v])=>v);
    const cur=scene(sid)||s;
    await hGroup("Analyse IA de la scène "+s.num,async()=>{
      await chunked(drop,5,e=>trk(base()+"/elements/"+e.id).delete());
      await chunked(add,5,f=>trk(base()+"/elements/"+uid()).set({sceneId:sid,cat:f.cat,name:f.name,src:"ai",by:S.me?.id||null,at:Date.now()},{before:null}));
      const patch={status:(drop.length||add.length)?"ai":(cur.status==="ok"?"ok":"ai"),analyzedAt:Date.now(),analyzedHash:sceneTextHash(cur)};
      if(!cur.synopsis&&typeof res?.synopsis==="string")patch.synopsis=res.synopsis.slice(0,400);
      await updateScene(sid,patch);});
    if(!opts.bulk)toast("Scène "+s.num+" : "+[add.length?add.length+" élément"+(add.length>1?"s":"")+" ajouté"+(add.length>1?"s":""):"",drop.length?drop.length+" retiré"+(drop.length>1?"s":""):""].filter(Boolean).join(", ")+(add.length||drop.length?".":"rien n'a changé."),4500);
    return"done";''')
R('''  const todo=S.scenes.filter(s=>!s.status||s.status==="todo").map(s=>s.id);if(!todo.length)return;''',
  '''  const todo=S.scenes.filter(needsAnalysis).map(s=>s.id);if(!todo.length)return;''')
R('''  const todo=S.scenes.filter(s=>!s.status||s.status==="todo").length;''', '''  const todo=S.scenes.filter(needsAnalysis).length;''')
R('''  const ai=$("#b-ai");if(ai)ai.onclick=()=>analyzeScene(s.id);''', '''  const ai=$("#b-ai");if(ai)ai.onclick=()=>confirmReanalyse(s.id);''')
# avertissement dans la scène quand le texte a changé depuis l'analyse
R('''          <span class="st ${st}">${STATUS[st]}</span>
        </div>''', '''          <span class="st ${st}">${STATUS[st]}</span>
          ${textChanged(s)?`<span class="st ai chg" title="Le scénario de cette scène a été modifié après l'analyse : relance l'IA pour mettre le dépouillement à jour">Texte modifié depuis l'analyse</span>`:""}
        </div>''')
t = re.sub(r'const APP_VERSION="1\.20\.\d";', 'const APP_VERSION="1.20.1";', t)
open(p, "w", encoding="utf-8").write(t); print("ok", p)
