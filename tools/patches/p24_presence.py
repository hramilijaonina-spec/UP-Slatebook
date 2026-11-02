# Présence des membres : où ils sont (onglet) et ce qu'ils modifient (plan du découpage, scène du scénario).
import re, sys
p = sys.argv[1]; t = open(p, encoding="utf-8").read()
def R(a, b, n=1):
    global t
    c = t.count(a)
    assert c == n, (a[:90], c)
    t = t.replace(a, b)

# --- envoyer l'onglet et la cellule en cours d'édition ---
R('''function sendPresence(){if(!S.room)return;S.room.presence({pid:S.pid||null,sid:S.sid||null,uid:S.me?.id||null}).catch(()=>{});}''',
  '''function sendPresence(){if(!S.room)return;PRES.tab=presTab();S.room.presence({pid:S.pid||null,sid:S.sid||null,uid:S.me?.id||null,tab:PRES.tab}).catch(()=>{});}
const PRES={tab:null,edit:null,offT:0,profs:{},want:new Set(),raf:0};
const presTab=()=>S.home||!S.pid?"home":(S.tab==="reports"?"scenes":S.tab);
function presEdit(v){clearTimeout(PRES.offT);if(PRES.edit===v)return;PRES.edit=v;S.room?.presence({edit:v}).catch(()=>{});}
document.addEventListener("focusin",e=>{const ta=e.target.closest?.("#dc textarea[data-f]");if(!ta)return;const tr=ta.closest("[data-id]");if(tr)presEdit("shot:"+tr.dataset.id);});
document.addEventListener("focusout",e=>{if(!e.target.closest?.("#dc"))return;clearTimeout(PRES.offT);
  PRES.offT=setTimeout(()=>{if(!document.activeElement?.closest?.("#dc textarea[data-f]"))presEdit(null);},1500);});
/* membres présents dans ce projet (sans moi) */
function presPeers(){
  return S.peers.filter(p=>p.kind==="viewer"&&!p.sameTab&&!p.isMe&&p.presence?.pid===S.pid&&S.pid&&(p.by||p.presence?.uid));
}
const PRES_COLORS=["#f07070","#4cc684","#f2934a","#ab8cf0","#6d9bf0","#e0a84a","#3cc4b8","#e2558a"];
function presProf(p){const id=p.by||p.presence?.uid;const pr=PRES.profs[id];
  if(!pr&&S.user&&!PRES.want.has(id)){PRES.want.add(id);S.user.profiles([id]).then(o=>{Object.assign(PRES.profs,o||{});renderPresence();}).catch(()=>{});}
  let h=0;for(const c of String(id))h=(h*31+c.charCodeAt(0))>>>0;
  return{id,name:pr?.name||"Quelqu'un",avatarUrl:pr?.avatarUrl||"",color:pr?.color||PRES_COLORS[h%PRES_COLORS.length]};}
const presAv=(pr,cls)=>`<span class="pav${cls?" "+cls:""}" style="--pc:${esc(pr.color)}" title="${esc(pr.name)}">${pr.avatarUrl?`<img src="${esc(pr.avatarUrl)}" alt="">`:esc((pr.name||"?").slice(0,1).toUpperCase())}</span>`;
function renderPresence(){
  if(PRES.raf)return;PRES.raf=requestAnimationFrame(()=>{PRES.raf=0;presDraw();});
}
function presDraw(){
  const peers=S.pid&&!S.home?presPeers():[];
  /* onglets : avatar de chaque membre sur l'onglet où il se trouve ; il clignote s'il est en train de modifier */
  ["script","dec","scenes","plan"].forEach(tk=>{const b=$("#tab-"+tk);if(!b)return;let box=b.querySelector(".tab-peers");
    const here=peers.filter(p=>(p.presence?.tab||"")===tk);
    if(!here.length){if(box)box.remove();return;}
    if(!box){box=document.createElement("span");box.className="tab-peers";b.append(box);}
    box.innerHTML=here.slice(0,3).map(p=>{const pr=presProf(p);const ed=!!(p.presence?.edit||p.presence?.editing);return presAv(pr,ed?"live":"");}).join("")+(here.length>3?`<span class="pav more">+${here.length-3}</span>`:"");
    box.title=here.map(p=>presProf(p).name+((p.presence?.edit||p.presence?.editing)?" modifie":" regarde")).join(" · ");});
  /* découpage : cadre lumineux autour du plan qu'un autre membre modifie */
  const wrap=$("#dc .dct-wrap");
  document.querySelectorAll(".peer-ring").forEach(r=>r.remove());
  if(wrap){const wr=wrap.getBoundingClientRect();
    for(const p of peers){const m=/^shot:(.+)$/.exec(p.presence?.edit||"");if(!m)continue;const tr=document.getElementById("dc-"+m[1]);if(!tr)continue;
      const rr=tr.getBoundingClientRect(),c0=(tr.querySelector(".dct-plan")||tr).getBoundingClientRect();const r={left:c0.left,top:rr.top,width:rr.right-c0.left,height:rr.height};const pr=presProf(p);const x=shotOfId(m[1]);
      const ring=document.createElement("div");ring.className="peer-ring";ring.style.setProperty("--pc",pr.color);
      ring.style.left=(r.left-wr.left+wrap.scrollLeft)+"px";ring.style.top=(r.top-wr.top+wrap.scrollTop)+"px";ring.style.width=r.width+"px";ring.style.height=r.height+"px";
      ring.innerHTML=`<span class="peer-tag">${presAv(pr,"live")}<span>${esc(pr.name)}${x?" · plan "+esc(shotNum(x)):""}</span></span>`;
      wrap.append(ring);}}
  /* scénario : la scène qu'un autre membre écrit */
  document.querySelectorAll(".ed-scene.peer-ed").forEach(s=>{s.classList.remove("peer-ed");s.style.removeProperty("--pc");s.querySelector(":scope>.peer-badge")?.remove();});
  for(const p of peers){const sid=p.presence?.editing;if(!sid)continue;const sec=document.querySelector(`.ed-scene[data-sid="${CSS.escape(sid)}"]`);if(!sec)continue;
    const pr=presProf(p);sec.classList.add("peer-ed");sec.style.setProperty("--pc",pr.color);
    const bd=document.createElement("span");bd.className="peer-badge";bd.innerHTML=presAv(pr,"live")+`<span>${esc(pr.name)} écrit</span>`;sec.prepend(bd);}
}
const shotOfId=id=>S.shots.find(x=>x.id===id);
addEventListener("resize",()=>renderPresence());
document.addEventListener("input",e=>{if(e.target.closest?.("#dc"))renderPresence();});
document.addEventListener("scroll",e=>{if(e.target.classList?.contains("dct-wrap"))renderPresence();},true);''')
R('''    room.onPeers(ch=>{S.peers=ch.peers;renderPeers();renderList();});''', '''    room.onPeers(ch=>{S.peers=ch.peers;renderPeers();renderList();renderPresence();});''')
R('''function render(){if(S.pid)snapSchedule();if(raf)return;raf=requestAnimationFrame(()=>{raf=0;renderTop();renderDesk();if(S.modalRefresh)S.modalRefresh();});}''',
  '''function render(){if(S.pid)snapSchedule();if(raf)return;raf=requestAnimationFrame(()=>{raf=0;renderTop();renderDesk();if(S.modalRefresh)S.modalRefresh();if(S.room&&PRES.tab!==presTab())sendPresence();presDraw();});}''')

# --- styles ---
R('''/* menu principal */''', '''/* présence des membres */
@keyframes pres-pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.55;transform:scale(.9)}}
@keyframes pres-glow{0%,100%{box-shadow:0 0 0 2px var(--pc),0 0 18px 4px color-mix(in srgb,var(--pc) 45%,transparent)}50%{box-shadow:0 0 0 1px color-mix(in srgb,var(--pc) 70%,transparent),0 0 8px 1px color-mix(in srgb,var(--pc) 20%,transparent)}}
.pav{display:inline-grid;place-items:center;width:20px;height:20px;border-radius:50%;overflow:hidden;border:2px solid var(--pc,var(--accent));background:var(--surface);color:var(--fg);font-size:10px;font-weight:700;flex:0 0 auto}
.pav img{width:100%;height:100%;object-fit:cover;display:block}
.pav.live{animation:pres-pulse 1.8s ease-in-out infinite}
.pav.more{border-color:var(--line-strong);font-size:9px}
.tabbar button{position:relative}
.tab-peers{position:absolute;top:3px;right:5px;display:flex;gap:0}
.tab-peers .pav{width:18px;height:18px;margin-left:-5px;box-shadow:0 0 0 2px var(--surface)}
.tab-peers .pav:first-child{margin-left:0}
.dct-wrap{position:relative}
.peer-ring{position:absolute;z-index:3;pointer-events:none;border-radius:6px;animation:pres-glow 1.8s ease-in-out infinite}
.peer-tag{position:absolute;left:6px;top:-11px;display:inline-flex;align-items:center;gap:5px;padding:1px 8px 1px 2px;border-radius:12px;background:var(--pc);color:#111;font-size:11px;font-weight:700;white-space:nowrap;box-shadow:0 2px 8px rgb(0 0 0 / .35)}
.peer-tag .pav{width:18px;height:18px;border-color:#fff;animation:none}
.ed-scene.peer-ed{border-radius:4px;animation:pres-glow 1.8s ease-in-out infinite}
.peer-badge{position:absolute;left:0;top:-22px;display:inline-flex;align-items:center;gap:5px;padding:1px 8px 1px 2px;border-radius:12px;background:var(--pc);color:#111;font-family:var(--f-ui);font-size:11px;font-weight:700;z-index:2}
.peer-badge .pav{width:18px;height:18px;border-color:#fff;animation:none}
@media (prefers-reduced-motion:reduce){.pav.live,.peer-ring,.ed-scene.peer-ed{animation:none}.peer-ring,.ed-scene.peer-ed{box-shadow:0 0 0 2px var(--pc),0 0 12px 2px color-mix(in srgb,var(--pc) 40%,transparent)}}
@media (max-width:760px){.tab-peers{top:2px;right:2px}.tab-peers .pav{width:15px;height:15px}}
/* menu principal */''')
t = re.sub(r'const APP_VERSION="1\.19\.\d";', 'const APP_VERSION="1.20.0";', t)
open(p, "w", encoding="utf-8").write(t); print("ok", p)
