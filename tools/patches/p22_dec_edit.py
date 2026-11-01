# Découpage : ne plus quitter l'édition ni déplacer la vue pendant qu'on tape.
import re, sys
p = sys.argv[1]; t = open(p, encoding="utf-8").read()
def R(a, b, n=1):
    global t
    c = t.count(a)
    assert c == n, (a[:90], c)
    t = t.replace(a, b)

# 1. le focus rendu après un rafraîchissement ne fait plus défiler la page
R('''  if(id){const n=document.getElementById(id);if(n&&n!==a){n.focus();if(val!==null)n.value=val;''',
  '''  if(id){const n=document.getElementById(id);if(n&&n!==a){n.focus({preventScroll:true});if(val!==null)n.value=val;''')

# 2. découpage : pas de redessin pendant qu'une cellule est en cours d'édition ; redessin seulement si quelque chose a changé ; défilement gardé
R('''function renderDecoupage(){
  const box=$("#dc");if(!box||!S.pid)return;
  const st=box.scrollTop;
  keepFocus(()=>{box.innerHTML=decEditHTML();});
  box.scrollTop=st;''', '''function decSig(){
  const im=v=>v?String(v).length+String(v).slice(-16):"";
  return JSON.stringify([S.pid,S.canWrite,S.aiOff,!!S.busy,DEC.showOpt,Number(P()?.targetSec)||0,!!scriptBackup(),[...DEC.ai],[...DEC.prog.entries()],
    S.scenes.map(s=>[s.id,s.num,s.heading,s.status,s.filmed]),
    S.shots.map(x=>[x.id,x.sceneId,x.pos,x.dur,x.type,x.move,x.angle,x.effect,x.action,x.sound,x.notes,x.done,im(x.img)])]);
}
const dcEditing=box=>{const a=document.activeElement;return !!(a&&box&&box.contains(a)&&a.matches("textarea,input,select"));};
/* pendant l'édition : on met seulement à jour les autres cellules (modifs des autres membres), sans toucher à celle où l'on tape */
function dcSoftUpdate(box){
  const a=document.activeElement;
  box.querySelectorAll("textarea[data-f]").forEach(el=>{if(el===a)return;const tr=el.closest("[data-id]");const x=tr&&S.shots.find(y=>y.id===tr.dataset.id);if(!x)return;
    const v=String(x[el.dataset.f]||"");if(el.value!==v){el.value=v;if(el.classList.contains("dc-hl-ta"))el.previousElementSibling.innerHTML=hlQuotes(v);dcGrow(el);}});
  box.querySelectorAll(".dc-donecb").forEach(c=>{const tr=c.closest("[data-id]");const x=tr&&S.shots.find(y=>y.id===tr.dataset.id);if(x&&c.checked!==!!x.done){c.checked=!!x.done;tr.classList.toggle("done",!!x.done);}});
}
function renderDecoupage(){
  const box=$("#dc");if(!box||!S.pid)return;
  if(box.childElementCount&&dcEditing(box)){DEC.renderPending=true;dcSoftUpdate(box);hButtons();return;}
  const sig=decSig();
  if(box.childElementCount&&box.dataset.sig===sig&&!DEC.focus){DEC.renderPending=false;hButtons();dcNavUpdate();return;}
  box.dataset.sig=sig;DEC.renderPending=false;
  const scEl=box.scrollHeight>box.clientHeight+1&&/(auto|scroll)/.test(getComputedStyle(box).overflowY)?box:dcScroller(box);
  const st=scEl.scrollTop,sl=box.querySelector(".dct-wrap")?.scrollLeft||0;
  keepFocus(()=>{box.innerHTML=decEditHTML();});
  const w=box.querySelector(".dct-wrap");if(w)w.scrollLeft=sl;''')
R('''function dcOpts(arr,val,pairs){''', '''/* quand on quitte l'édition, on applique les changements mis de côté */
document.addEventListener("focusout",e=>{if(!DEC.renderPending||!e.target.closest?.("#dc"))return;
  setTimeout(()=>{if(DEC.renderPending&&!dcEditing($("#dc")))render();},120);});
function dcOpts(arr,val,pairs){''')

# 3. l'en-tête ne se replie pas quand le clavier s'ouvre (le défilement vient alors du clavier, pas de l'utilisateur)
R('''    if(el.closest&&el.closest(".scrim,.pop,.dc-pop,.sc-drop,.cop-panel,.projbar,.tabbar"))return;''',
  '''    if(el.closest&&el.closest(".scrim,.pop,.dc-pop,.sc-drop,.cop-panel,.projbar,.tabbar"))return;
    const ae=document.activeElement;if(ae&&ae.matches&&ae.matches("textarea,input,select,[contenteditable]"))return;''')

R('''  box.querySelectorAll("textarea.dc-grow").forEach(dcGrow);
  DEC.navOpen=false;dcNavUpdate(true);''', '''  DEC.navOpen=false;dcNavDraw();
  box.querySelectorAll("textarea.dc-grow").forEach(dcGrow);
  scEl.scrollTop=st;
  dcNavUpdate(true);''')
t = re.sub(r'const APP_VERSION="1\.18\.\d";', 'const APP_VERSION="1.18.3";', t)
open(p, "w", encoding="utf-8").write(t); print("ok", p)
