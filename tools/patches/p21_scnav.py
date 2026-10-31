# Téléphone, découpage : navigation rapide entre scènes (barre collante ◀ scène ▾ ▶ + liste).
import re, sys
p = sys.argv[1]; t = open(p, encoding="utf-8").read()
def R(a, b, n=1):
    global t
    c = t.count(a)
    assert c == n, (a[:90], c)
    t = t.replace(a, b)

R('''    const seq=`<td class="dct-seq" rowspan="${rows}">''', '''    const seq=`<td class="dct-seq" data-sid="${esc(s.id)}" rowspan="${rows}">''')
R('''  return bar+`<div class="dc-inner">${note}${table}</div>`;''', '''  return bar+(S.scenes.length?`<div class="dc-scnav" id="dc-scnav"></div>`:"")+`<div class="dc-inner">${note}${table}</div>`;''')
R('''  box.querySelectorAll("textarea.dc-grow").forEach(dcGrow);
  if(DEC.focus){''', '''  box.querySelectorAll("textarea.dc-grow").forEach(dcGrow);
  DEC.navOpen=false;dcNavUpdate(true);
  if(DEC.focus){''')
R('''function dcOpts(arr,val,pairs){''', '''/* ---------- téléphone : aller vite d'une scène à l'autre dans le découpage ---------- */
const DCNAV_ICON={prev:`<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 6l-6 6 6 6"/></svg>`,next:`<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg>`,
  down:`<svg class="chev" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>`};
function dcAnchors(){return[...document.querySelectorAll("#dc td.dct-seq[data-sid]")];}
function dcScroller(el){let n=el&&el.parentElement;while(n&&n!==document.body){const o=getComputedStyle(n).overflowY;if((o==="auto"||o==="scroll")&&n.scrollHeight>n.clientHeight+1)return n;n=n.parentElement;}return document.scrollingElement;}
function dcCurrent(){
  const nav=$("#dc-scnav");const as=dcAnchors();if(!as.length)return null;
  const lim=(nav?nav.getBoundingClientRect().bottom:0)+24;let cur=as[0];
  for(const a of as){if(a.closest("tr").getBoundingClientRect().top<=lim)cur=a;else break;}
  return cur.dataset.sid;
}
function dcJump(sid){
  const a=document.querySelector(`#dc td.dct-seq[data-sid="${CSS.escape(sid)}"]`);if(!a)return;
  const tr=a.closest("tr"),nav=$("#dc-scnav"),sc=dcScroller(tr);
  const off=(nav?nav.getBoundingClientRect().height:0)+8;
  const top=sc===document.scrollingElement?tr.getBoundingClientRect().top+scrollY:tr.getBoundingClientRect().top-sc.getBoundingClientRect().top+sc.scrollTop;
  DEC.navSid=sid;DEC.navLock=Date.now();
  sc.scrollTo({top:Math.max(0,top-off-(nav&&nav.offsetTop>0&&sc!==document.scrollingElement?0:0)),behavior:"smooth"});
  dcNavDraw();
}
function dcNavUpdate(force){
  const nav=$("#dc-scnav");if(!nav)return;
  if(!force&&DEC.navLock&&Date.now()-DEC.navLock<900)return;
  const sid=dcCurrent()||S.scenes[0]?.id;
  if(force||sid!==DEC.navSid){DEC.navSid=sid;if(!DEC.navOpen||force)dcNavDraw();}
}
function dcNavDraw(){
  const nav=$("#dc-scnav");if(!nav)return;
  const i=Math.max(0,S.scenes.findIndex(s=>s.id===DEC.navSid));const s=S.scenes[i];if(!s){nav.innerHTML="";return;}
  const meta=sc=>{const all=shotsOf(sc.id);const l=all.filter(x=>!isOpt(x));return l.length+" plan"+(l.length>1?"s":"")+" · "+fmtDur(sumDur(l));};
  nav.classList.toggle("open",!!DEC.navOpen);
  nav.innerHTML=`<button type="button" class="dcn-arrow" data-go="-1" aria-label="Scène précédente" ${i<=0?"disabled":""}>${DCNAV_ICON.prev}</button>
    <button type="button" class="dcn-cur" aria-expanded="${!!DEC.navOpen}" aria-label="Scène ${esc(s.num)} : ${esc(s.heading)}. Choisir une autre scène">
      <b>${esc(s.num)}</b><span><span class="hd">${esc(s.heading)}</span><small>${esc(meta(s))} · ${i+1}/${S.scenes.length}</small></span>${DCNAV_ICON.down}</button>
    <button type="button" class="dcn-arrow" data-go="1" aria-label="Scène suivante" ${i>=S.scenes.length-1?"disabled":""}>${DCNAV_ICON.next}</button>
    ${DEC.navOpen?`<div class="dcn-list" role="listbox" aria-label="Scènes">${S.scenes.map((x,k)=>`<button type="button" role="option" class="dcn-it" data-sid="${esc(x.id)}" aria-selected="${k===i}"><span class="band" style="background:${bandColor(x)}"></span><b>${esc(x.num)}</b><span class="hd">${esc(x.location||x.heading)}<small>${esc(meta(x))}</small></span>${progHTML(x)}</button>`).join("")}</div>`:""}`;
  nav.querySelectorAll(".dcn-arrow").forEach(b=>b.onclick=()=>{const j=i+Number(b.dataset.go);if(S.scenes[j]){DEC.navOpen=false;dcJump(S.scenes[j].id);}});
  nav.querySelector(".dcn-cur").onclick=()=>{DEC.navOpen=!DEC.navOpen;dcNavDraw();if(DEC.navOpen){const l=nav.querySelector(".dcn-list"),c=nav.querySelector('.dcn-it[aria-selected="true"]');if(l&&c)l.scrollTop=Math.max(0,c.offsetTop-l.clientHeight/2);}};
  nav.querySelectorAll(".dcn-it").forEach(b=>b.onclick=()=>{DEC.navOpen=false;dcJump(b.dataset.sid);});
}
document.addEventListener("scroll",()=>{if(S.tab!=="dec"||!$("#dc-scnav"))return;if(DEC.navRaf)return;DEC.navRaf=requestAnimationFrame(()=>{DEC.navRaf=0;dcNavUpdate();});},true);
document.addEventListener("click",e=>{if(DEC.navOpen&&e.target.isConnected&&!e.target.closest("#dc-scnav")){DEC.navOpen=false;dcNavDraw();}});
document.addEventListener("keydown",e=>{if(DEC.navOpen&&e.key==="Escape"){DEC.navOpen=false;dcNavDraw();}});
function dcOpts(arr,val,pairs){''')
R('''/* menu principal */''', '''/* navigation entre scènes du découpage (téléphone) */
.dc-scnav{display:none}
@media (max-width:760px){
  .desk .dc{overflow:visible}
  .desk .dc-bar{position:static}
  .dc-scnav{display:flex;align-items:stretch;gap:6px;position:sticky;top:0;z-index:6;padding:6px 8px;margin:0 -1px;background:var(--surface);border-bottom:1px solid var(--line);box-shadow:0 4px 12px rgb(0 0 0 / .25)}
  .dcn-arrow{flex:0 0 auto;width:44px;border:1px solid var(--line-strong);background:var(--sunk);border-radius:8px;color:var(--fg);display:grid;place-items:center}
  .dcn-arrow:disabled{opacity:.35}
  .dcn-arrow svg,.dcn-cur svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}
  .dcn-cur{flex:1;min-width:0;display:flex;align-items:center;gap:10px;border:1px solid var(--line-strong);background:var(--sunk);border-radius:8px;padding:6px 10px;text-align:left;color:var(--fg)}
  .dcn-cur>b{font-family:var(--f-display);font-size:24px;line-height:1;color:var(--t-dec)}
  .dcn-cur>span{flex:1;min-width:0;display:flex;flex-direction:column}
  .dcn-cur .hd{font-weight:700;font-size:12.5px;text-transform:uppercase;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .dcn-cur small{color:var(--muted);font-size:11.5px;font-variant-numeric:tabular-nums}
  .dc-scnav.open .dcn-cur .chev{transform:rotate(180deg)}
  .dcn-list{position:absolute;left:8px;right:8px;top:calc(100% - 2px);max-height:min(62vh,520px);overflow:auto;overscroll-behavior:contain;background:var(--surface);border:1px solid var(--line-strong);border-radius:0 0 10px 10px;box-shadow:0 14px 36px rgb(0 0 0 / .45)}
  .dcn-it{display:grid;grid-template-columns:6px 34px minmax(0,1fr) auto;gap:10px;align-items:center;width:100%;border:0;border-bottom:1px solid var(--line);background:transparent;padding:10px 10px 10px 0;text-align:left;color:var(--fg)}
  .dcn-it .band{align-self:stretch;margin-block:-10px}
  .dcn-it b{font-family:var(--f-display);font-size:20px;text-align:right}
  .dcn-it .hd{font-weight:600;font-size:12.5px;text-transform:uppercase;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .dcn-it .hd small{display:block;font-weight:500;text-transform:none;color:var(--muted);font-size:11.5px}
  .dcn-it[aria-selected=true]{background:var(--accent-soft)}
}
/* menu principal */''')
t = re.sub(r'const APP_VERSION="1\.18\.\d";', 'const APP_VERSION="1.18.1";', t)
open(p, "w", encoding="utf-8").write(t); print("ok", p)
