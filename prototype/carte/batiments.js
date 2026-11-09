// Construction des bâtiments de la carte d'Aubagne (toits, façades, couleurs lues sur la photo).
// Ce fichier sert deux fois : chargé par la page (secours) et lancé en arrière-plan (« worker ») pour que
// la carte reste fluide pendant qu'on se déplace. Il ne touche ni à la scène ni à la page.
if(typeof document==='undefined'&&typeof importScripts==='function')importScripts('https://cdn.jsdelivr.net/npm/three@0.147.0/build/three.min.js');
(function(){
const PAL={
  maison:[['#ead9b8','#e3cba0','#efe2c8','#dcc395','#f1d7ae'],['#b5562f','#a84d2a','#bf6539','#b0603c']],
  immeuble:[['#e6ddd0','#d9d0c0','#efe7d8','#e4d4b8'],['#a29c90','#9a948a','#b0623e']],
  industrie:[['#c9c6bf','#bdbab3','#d2cbbd'],['#8e9296','#a7aaa8','#9aa0a4']],
  commerce:[['#e0d8c8','#d6cfc2'],['#a19d94','#b4b0a6']],
  public:[['#ead8b2','#e4cfa4'],['#b5562f','#a9a49a']],
  religieux:[['#eadfc6'],['#a8502c']],
  annexe:[['#cdbf9f','#c2b394'],['#8e7e66','#9a6b4c']],
  autre:[['#e3d3b2','#dccaa6','#e9dcc2'],['#b5562f','#a8a297']],
};
// façades : matériau des murs de la BD TOPO (codes des fichiers fonciers : 1 pierre, 2 meulière, 3 béton, 4 briques,
// 5 aggloméré, 6 bois ; deux chiffres = deux matériaux), sinon la couleur OpenStreetMap, sinon la palette d'Aubagne
const PAL_AUBAGNE=['#ebd3a2','#e2bd84','#d9aa6e','#f0e2c4','#e9d7b2','#e8c6aa','#ddb59b','#f1ece0','#e8e2d3','#eedcb6'];
const PAL_MAT={1:['#d8c9aa','#cdbd9c','#e0d3b6','#c6b595'],2:['#c49a6c','#b98d60','#cfa877'],3:['#d0cbc1','#c4bfb4','#dad4c8','#bdb8ae'],
  4:['#b5644a','#a95a42','#c07456'],5:['#c2beb6','#b5b1a9'],6:['#8d6b4b','#9a7754','#7f5f42']};
// toits, quand la photo manque : 1 tuiles, 2 ardoises, 3 zinc ou aluminium, 4 béton
const PAL_TOIT={1:['#b5562f','#a84d2a','#bf6539','#b0603c'],2:['#5f636a','#6a6e73'],3:['#9aa0a4','#a7aaa8','#8e9296'],4:['#b8b3a8','#aaa59b']};
const pick=(a,r=Math.random)=>a[(r()*a.length)|0];
const chiffres=(v,max)=>[Math.floor(v/10)%10,v%10].filter(x=>x>=1&&x<=max);
function couleurMur(genre,murs,r=Math.random){
  const d=chiffres(murs,6),m=d.length?d[(r()*d.length)|0]:0,habite=genre==='maison'||genre==='immeuble';
  if(m===1||m===2||m===6)return pick(PAL_MAT[m],r);
  if(m===3)return habite||genre==='public'||genre==='autre'?pick(PAL_AUBAGNE,r):pick(PAL_MAT[3],r);
  if(m===4)return genre==='industrie'||genre==='annexe'||r()<.15?pick(PAL_MAT[4],r):pick(PAL_AUBAGNE,r);   // en Provence, la brique est presque toujours enduite
  if(m===5)return genre==='industrie'||genre==='annexe'?pick(PAL_MAT[5],r):pick(PAL_AUBAGNE,r);
  if(genre==='religieux')return pick(PAL_MAT[1],r);
  if(habite||genre==='autre')return pick(PAL_AUBAGNE,r);
  return pick((PAL[genre]||PAL.autre)[0],r);
}
function couleurToit(genre,toit,r=Math.random){const d=chiffres(toit,4);return d.length?pick(PAL_TOIT[d[(r()*d.length)|0]],r):pick((PAL[genre]||PAL.autre)[1],r);}
const ADOUCIR=new THREE.Color('#d8cfc0');
function couleurOSM(s){
  s=String(s||'').split(';')[0].trim().toLowerCase().replace(/[\s_-]/g,'');
  let c=null;
  if(/^#?([0-9a-f]{3}|[0-9a-f]{6})$/.test(s))c=new THREE.Color(s[0]==='#'?s:'#'+s);
  else if(THREE.Color.NAMES&&THREE.Color.NAMES[s]!==undefined)c=new THREE.Color(THREE.Color.NAMES[s]);
  return c&&c.lerp(ADOUCIR,.15);   // évite les blancs et rouges purs
}
let COULS=[],GENRES=[],CB=[],BH=0,iM=-1,iT=-1,iC=-1,iCT=-1,iE=-1,iF=-1;
// tirage au sort propre à chaque bâtiment : le même à chaque reconstruction du carré (couleurs, volets, forme du toit)
function aleaBat(b,BH){
  let h=(Math.imul(Math.round(b[BH]*10),73856093)^Math.imul(Math.round(b[BH+1]*10),19349663))|0;
  return ()=>{h=h+0x6D2B79F5|0;let x=Math.imul(h^h>>>15,1|h);x=x+Math.imul(x^x>>>7,61|x)^x;return((x^x>>>14)>>>0)/4294967296;};
}
// ---------- toits en pente : rectangle qui enveloppe le bâtiment, pans du toit, découpage ----------
function dansPoly(x,z,xs,zs){
  let ok=false;for(let i=0,j=xs.length-1;i<xs.length;j=i++)if((zs[i]>z)!==(zs[j]>z)&&x<xs[i]+(z-zs[i])*(xs[j]-xs[i])/(zs[j]-zs[i]))ok=!ok;return ok;
}
// plus petit rectangle orienté qui contient le contour : e = sens du faîtage (grand côté), n = sa perpendiculaire
function rectOriente(xs,zs){
  const P=xs.map((x,i)=>[x,zs[i]]).sort((a,b)=>a[0]-b[0]||a[1]-b[1]),cr=(o,a,b)=>(a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0]),lo=[],up=[];
  for(const p of P){while(lo.length>=2&&cr(lo[lo.length-2],lo[lo.length-1],p)<=0)lo.pop();lo.push(p);}
  for(let i=P.length-1;i>=0;i--){const p=P[i];while(up.length>=2&&cr(up[up.length-2],up[up.length-1],p)<=0)up.pop();up.push(p);}
  const H=lo.slice(0,-1).concat(up.slice(0,-1));
  let best=null;
  for(let i=0;i<H.length;i++){const a=H[i],b=H[(i+1)%H.length];let ex=b[0]-a[0],ez=b[1]-a[1];const l=Math.hypot(ex,ez);if(l<1e-6)continue;ex/=l;ez/=l;
    let u0=1e9,u1=-1e9,v0=1e9,v1=-1e9;
    for(const p of H){const v=p[0]*ex+p[1]*ez,u=-p[0]*ez+p[1]*ex;if(v<v0)v0=v;if(v>v1)v1=v;if(u<u0)u0=u;if(u>u1)u1=u;}
    const ar=(v1-v0)*(u1-u0);if(!best||ar<best.ar)best={ar,ex,ez,u0,u1,v0,v1};}
  if(!best)return null;
  let {ex,ez,u0,u1,v0,v1}=best,hl=(v1-v0)/2,hw=(u1-u0)/2,nx=-ez,nz=ex;
  const cv=(v0+v1)/2,cu=(u0+u1)/2,cx=cv*ex-cu*ez,cz=cv*ez+cu*ex;
  if(hw>hl){[hl,hw]=[hw,hl];[ex,ez,nx,nz]=[nx,nz,-ex,-ez];}
  return {cx,cz,ex,ez,nx,nz,hl,hw,ar:best.ar};
}
// pans du toit : des plans y = A x + B z + C ; le toit est le plus bas d'entre eux en chaque point
// (2 = deux pans, 3 = quatre pans, 4 = pyramide, 5 = un pan)
function plansToit(Q,forme,gout,rise){
  const pl=(wx,wz,d,s)=>[-s*wx,-s*wz,gout+s*d+s*(wx*Q.cx+wz*Q.cz)];
  if(forme===5)return [pl(Q.nx,Q.nz,Q.hw,rise/(2*Q.hw))];
  const sA=rise/Q.hw,P=[pl(Q.nx,Q.nz,Q.hw,sA),pl(-Q.nx,-Q.nz,Q.hw,sA)];
  if(forme===3||forme===4){const sB=forme===4?rise/Q.hl:sA;P.push(pl(Q.ex,Q.ez,Q.hl,sB),pl(-Q.ex,-Q.ez,Q.hl,sB));}
  return P;
}
// garde la partie du polygone où a x + b z + c <= 0
function couperDemi(poly,a,b,c){
  const out=[],n=poly.length;
  for(let i=0;i<n;i++){const p=poly[i],q=poly[(i+1)%n],fp=a*p[0]+b*p[1]+c,fq=a*q[0]+b*q[1]+c;
    if(fp<=0)out.push(p);
    if((fp<0&&fq>0)||(fp>0&&fq<0)){const t=fp/(fp-fq);out.push([p[0]+(q[0]-p[0])*t,p[1]+(q[1]-p[1])*t]);}}
  return out;
}
function nettoyerPoly(pg){
  const out=[];for(const p of pg){const q=out[out.length-1];if(!q||Math.hypot(p[0]-q[0],p[1]-q[1])>1e-3)out.push(p);}
  while(out.length>1&&Math.hypot(out[0][0]-out[out.length-1][0],out[0][1]-out[out.length-1][1])<=1e-3)out.pop();
  return out;
}
// forme du toit : 1 plat, 2 deux pans, 3 quatre pans, 4 pyramide, 5 un pan.
// D'après OpenStreetMap (roof:shape), la hauteur du toit et le matériau BD TOPO, et ce que montre la photo (tuiles rouges ou toit gris)
function formeDuToit(genre,aireP,Q,ecart,matT,osmF,info,r){
  if(!Q||Q.hw<1.2||aireP<6||osmF===1)return 1;
  const dm=chiffres(matT,4),tuile=dm.includes(1)||dm.includes(2),beton=dm.includes(4)&&!tuile,rouge=info?info.rouge:-1;
  let pente;
  if(osmF>=2)pente=true;
  else if(genre==='industrie'||genre==='commerce')pente=(ecart>=1&&aireP<400)||(rouge>=.4&&aireP<600);
  else if(genre==='immeuble')pente=((ecart>=1||tuile||rouge>=.35)&&aireP<900&&!beton);
  else pente=(aireP<(ecart>=1.5?2500:900)&&!beton)||(rouge>=.35&&aireP<1500);
  // la photo montre un toit gris sans tuiles et la BD TOPO ne donne pas de pente : toit-terrasse
  if(pente&&!osmF&&ecart<.5&&!tuile&&info&&rouge>=0&&rouge<.08&&info.gris>=.5)pente=false;
  if(!pente)return 1;
  if(osmF>=2)return osmF;
  if(genre==='annexe'&&aireP<40)return 5;
  if(Q.hl/Q.hw>1.7)return r()<.8?2:3;
  return r()<.65?3:2;
}
// couleur des murs lue sur la photo (façade vue de biais), éclaircie un peu (voile de la photo) et mêlée à la palette
function murPhoto(c,base){
  const col=new THREE.Color(c[0]/255,c[1]/255,c[2]/255),hsl={};col.getHSL(hsl);
  col.setHSL(hsl.h,Math.min(.42,hsl.s*1.2),Math.min(.88,Math.max(.6,hsl.l*1.1+.06)));
  return (typeof base==='string'?new THREE.Color(base):base.clone()).lerp(col,.75);
}
// lit la photo fine d'un carré pour chacun de ses bâtiments : dedans, la couleur du toit (part de tuiles rouges, part de gris) ;
// autour (de 0,7 à 1,6 m du mur), la façade que la photo montre souvent de biais : couleurs claires, peu saturées, sans végétation ni ombre
function lirePhoto(liste,d,W,H,rect){
  const [rx,rz,rw,rd]=rect,m=[];
  const lire=(x,z)=>{const i=Math.floor((x-rx)/rw*W),j=Math.floor((z-rz)/rd*H);return i<0||j<0||i>=W||j>=H?-1:(j*W+i)*4;};
  for(const b of liste){
    const n=(b.length-BH)/2,xs=[],zs=[];let a=0,x0=1e9,x1=-1e9,z0=1e9,z1=-1e9;
    for(let i=0;i<n;i++){const x=b[BH+2*i],z=b[BH+1+2*i];xs.push(x);zs.push(z);if(x<x0)x0=x;if(x>x1)x1=x;if(z<z0)z0=z;if(z>z1)z1=z;}
    for(let i=0;i<n;i++){const j=(i+1)%n;a+=xs[i]*zs[j]-xs[j]*zs[i];}
    const sg=a>0?-1:1,pas=Math.max(.5,Math.sqrt((x1-x0)*(z1-z0)/60));
    let tot=0,ro=0,gr=0;const s=[0,0,0],sr=[0,0,0];
    for(let x=x0+pas/2;x<x1;x+=pas)for(let z=z0+pas/2;z<z1;z+=pas){
      if(!dansPoly(x,z,xs,zs))continue;const o=lire(x,z);if(o<0)continue;
      const R0=d[o],G0=d[o+1],B0=d[o+2],mx=Math.max(R0,G0,B0),mn=Math.min(R0,G0,B0);
      tot++;s[0]+=R0;s[1]+=G0;s[2]+=B0;
      if(R0>G0*1.1&&R0>B0*1.25&&R0>70){ro++;sr[0]+=R0;sr[1]+=G0;sr[2]+=B0;}else if(mx-mn<mx*.14+4)gr++;
    }
    const fac=[];
    for(let i=0;i<n&&fac.length<400;i++){
      const j=(i+1)%n,ex=xs[j]-xs[i],ez=zs[j]-zs[i],L=Math.hypot(ex,ez);if(L<1)continue;
      const nx=-ez/L*sg,nz=ex/L*sg;
      for(let t=.6;t<L-.3;t+=1.2)for(const off of [.7,1.6]){
        const x=xs[i]+ex/L*t+nx*off,z=zs[i]+ez/L*t+nz*off;if(dansPoly(x,z,xs,zs))continue;const o=lire(x,z);if(o<0)continue;
        const R0=d[o],G0=d[o+1],B0=d[o+2],mx=Math.max(R0,G0,B0),mn=Math.min(R0,G0,B0),lum=(R0+G0+B0)/3;
        if(lum>105&&mx-mn<mx*.38&&G0<=R0+6&&B0<=R0+4&&!(R0>G0*1.12&&R0>B0*1.3))fac.push([R0,G0,B0,lum]);
      }
    }
    const e={rouge:tot?ro/tot:-1,gris:tot?gr/tot:0,toit:null,mur:null};
    if(ro>=3&&ro>=tot*.3)e.toit=sr.map(c=>c/ro);else if(tot)e.toit=s.map(c=>c/tot);
    if(fac.length>=6){fac.sort((p,q)=>q[3]-p[3]);const k=Math.max(4,Math.ceil(fac.length*.6)),c=[0,0,0];for(let i=0;i<k;i++)for(let q=0;q<3;q++)c[q]+=fac[i][q];e.mur=c.map(x=>x/k);}
    m.push(e);
  }
  return m;
}
  const TEINTES_TUILE=['#c9854f','#8a5a43','#c4502c','#b07a5a'].map(h=>new THREE.Color(h).convertSRGBToLinear());   // ocre, brun, rouge vif, rosé
  const STYLE={maison:1,immeuble:2,commerce:3,industrie:4,public:5,religieux:6,annexe:0},ETAGE={1:2.9,2:2.95,3:3.6,4:5,5:3.6,6:6};
// réglages venus de ville.json
function preparer(cfg){
  GENRES=cfg.genres;CB=cfg.champsBat;BH=CB.length;COULS=(cfg.couleursBat||[]).map(couleurOSM);
  iM=CB.indexOf('murs');iT=CB.indexOf('toiture');iC=CB.indexOf('couleur');iCT=CB.indexOf('couleur_toit');iE=CB.indexOf('etages');iF=CB.indexOf('forme_toit');
}
const osm=(b,i)=>i>=0&&b[i]>0?COULS[b[i]-1]||null:null;
// tous les bâtiments d'un carré : renvoie les tableaux prêts pour la carte graphique
function construire(liste,ph){
    const P=[],N=[],C=[],TT=[],FA=[],FB=[],I=[];let v=0;
    const sommet=(x,y,z,nx,ny,nz,c,k,toit,a0,a1,a2,a3,b0,b1,b2,b3)=>{
      P.push(x,y,z);N.push(nx,ny,nz);C.push(Math.min(255,c.r*255*k),Math.min(255,c.g*255*k),Math.min(255,c.b*255*k));TT.push(toit);FA.push(a0,a1,a2,a3);FB.push(b0,b1,b2,b3);return v++;};
    const unBat=(b,kb)=>{
      // bas des murs sous le terrain, gouttière et faîtage à leur altitude réelle (BD TOPO) : ni flottant, ni enfoncé
      const r=aleaBat(b,BH),bot=b[0],sol=bot+1.5,gout=b[1],ecart=b[2]-b[1],genre=GENRES[b[3]],et=iE>=0?b[iE]:0,n=(b.length-BH)/2;
      const xs=[],zs=[];for(let i=0;i<n;i++){xs.push(b[BH+2*i]);zs.push(b[BH+1+2*i]);}
      let a=0;for(let i=0;i<n;i++){const j=(i+1)%n;a+=xs[i]*zs[j]-xs[j]*zs[i];}
      if(a>0){xs.reverse();zs.reverse();}
      const aireP=Math.abs(a)/2,info=ph&&ph[kb],oc=osm(b,iC),oct=osm(b,iCT),matT=iT>=0?b[iT]:0,shade=.92+r()*.14;
      let wc=oc||couleurMur(genre,iM>=0?b[iM]:0,r);
      if(!oc&&info&&info.mur)wc=murPhoto(info.mur,wc);
      if(typeof wc==='string')wc=new THREE.Color(wc);
      const Q=n>=3?rectOriente(xs,zs):null,forme=formeDuToit(genre,aireP,Q,ecart,matT,iF>=0?b[iF]:0,info,r);
      // couleur du toit, en couleurs « réelles » comme la photo : lue sur la photo, sinon OpenStreetMap, sinon le matériau BD TOPO
      let rc;
      if(oct)rc=oct.clone().convertSRGBToLinear();
      else if(info&&info.toit&&(forme===1||info.rouge>=.3||info.gris>=.5))rc=new THREE.Color(info.toit[0]/255,info.toit[1]/255,info.toit[2]/255).convertSRGBToLinear();
      else rc=new THREE.Color(forme>1&&!chiffres(matT,4).length?pick(PAL_TOIT[1],r):couleurToit(genre,matT,r)).convertSRGBToLinear();
      // façade : style, volets (couleurs provençales), hauteur d'un étage, mur de la porte (le plus long)
      const st=genre==='autre'?(aireP>300?5:1):STYLE[genre]??1;
      // chaque toit a sa teinte : plus ou moins clair, et sans photo, tiré vers l'ocre, le brun ou le rouge vif
      {const fp=!!(info&&info.toit)||!!oct,va=fp?.08:.16;rc.multiplyScalar(1-va+2*va*r());
       if(!fp)rc.lerp(pick(TEINTES_TUILE,r),r()*.35);}
      const sd=r()*255|0,ech=.9+r()*.2;   // graine du toit (tuiles dépareillées, taches, lichen) et taille des tuiles
      const vol=st===1||st===3?1+(r()*7|0):st===2&&r()<.7?1+(r()*7|0):0;
      const hm=Math.max(0,gout-sol),fh=et>0&&hm>2?Math.min(4.5,Math.max(2.6,hm/et)):ETAGE[st]||3,hmC=Math.min(255,Math.round(hm*4));
      let lg=-1,iP=0;for(let i=0;i<n;i++){const j=(i+1)%n,l=Math.hypot(xs[j]-xs[i],zs[j]-zs[i]);if(l>lg){lg=l;iP=i;}}
      let plans=null;
      if(forme>1){
        let rise=forme===5?(ecart>=.5?Math.min(ecart,Q.hw*1.2):Q.hw*.36):(ecart>=.5?Math.min(ecart,Q.hw*1.1):Q.hw*.32);
        plans=plansToit(Q,forme,gout,Math.max(.4,rise));
      }
      const parapet=forme===1&&aireP>60&&st>=2&&st<=5?(st===4?.4:.6):0;   // acrotère autour des toits-terrasses
      const yPlat=(gout+b[2])/2,hTop=(x,z)=>{if(!plans)return yPlat+parapet;let h=1e9;for(const q of plans){const y=q[0]*x+q[1]*z+q[2];if(y<h)h=y;}return h;};
      // murs : coupés là où le toit change de pan, pour monter exactement jusqu'au toit (pignons)
      for(let i=0;i<n;i++){
        const j=(i+1)%n,ex=xs[j]-xs[i],ez=zs[j]-zs[i],L=Math.hypot(ex,ez)||1,nx=-ez/L,nz=ex/L,ts=[0,1],porte=i===iP?1:0;
        if(plans&&plans.length>1)for(let k=0;k<plans.length;k++)for(let q=k+1;q<plans.length;q++){
          const A=plans[k][0]-plans[q][0],Bq=plans[k][1]-plans[q][1],Cq=plans[k][2]-plans[q][2],g0=A*xs[i]+Bq*zs[i]+Cq,g1=A*xs[j]+Bq*zs[j]+Cq;
          if(g0*g1<0)ts.push(g0/(g0-g1));}
        ts.sort((p,q)=>p-q);
        for(let k=0;k<ts.length-1;k++){
          const t0=ts[k],t1=ts[k+1];if(t1-t0<1e-6)continue;
          const xa=xs[i]+ex*t0,za=zs[i]+ez*t0,xb=xs[i]+ex*t1,zb=zs[i]+ez*t1,ya=hTop(xa,za),yb=hTop(xb,zb);
          const s0=sommet(xa,bot,za,nx,0,nz,wc,shade,0,t0*L,bot-sol,L,fh,st,vol,porte,hmC);
          sommet(xb,bot,zb,nx,0,nz,wc,shade,0,t1*L,bot-sol,L,fh,st,vol,porte,hmC);
          sommet(xb,yb,zb,nx,0,nz,wc,shade,0,t1*L,yb-sol,L,fh,st,vol,porte,hmC);
          sommet(xa,ya,za,nx,0,nz,wc,shade,0,t0*L,ya-sol,L,fh,st,vol,porte,hmC);
          I.push(s0,s0+1,s0+2,s0,s0+2,s0+3);
        }
      }
      if(!plans){   // toit plat : la photo
        const r0=v,tris=THREE.ShapeUtils.triangulateShape(xs.map((x,i)=>new THREE.Vector2(x,zs[i])),[]);
        for(let i=0;i<n;i++)sommet(xs[i],yPlat,zs[i],0,1,0,rc,shade,1,0,0,0,0,0,0,0,0);
        for(const [p0,p1,p2] of tris){const cy=(zs[p1]-zs[p0])*(xs[p2]-xs[p0])-(xs[p1]-xs[p0])*(zs[p2]-zs[p0]);cy>0?I.push(r0+p0,r0+p1,r0+p2):I.push(r0+p0,r0+p2,r0+p1);}
        return;
      }
      // toit en pente : bâtiment presque rectangulaire → toit sur le rectangle avec un débord de 40 cm ; sinon sur le contour
      let poly;
      if(aireP/(4*Q.hl*Q.hw)>.88){const o=.4,L2=Q.hl+o,W2=Q.hw+o,{cx,cz,ex,ez,nx,nz}=Q;
        poly=[[cx+ex*L2+nx*W2,cz+ez*L2+nz*W2],[cx-ex*L2+nx*W2,cz-ez*L2+nz*W2],[cx-ex*L2-nx*W2,cz-ez*L2-nz*W2],[cx+ex*L2-nx*W2,cz+ez*L2-nz*W2]];}
      else poly=xs.map((x,i)=>[x,zs[i]]);
      for(let k=0;k<plans.length;k++){
        let pg=poly;
        for(let q=0;q<plans.length&&pg.length>=3;q++)if(q!==k)pg=couperDemi(pg,plans[k][0]-plans[q][0],plans[k][1]-plans[q][1],plans[k][2]-plans[q][2]);
        pg=nettoyerPoly(pg);if(pg.length<3)continue;
        // tuiles : colonnes dans le sens de la pente, à leur vraie taille sur le pan incliné
        const [A,Bp,Cp]=plans[k],g=Math.hypot(A,Bp)||1e-6,dx=-A/g,dz=-Bp/g,tx=-dz,tz=dx,kk=Math.sqrt(1+g*g),nl=Math.hypot(A,1,Bp);
        const tris=THREE.ShapeUtils.triangulateShape(pg.map(p=>new THREE.Vector2(p[0],p[1])),[]),r0=v;
        for(const [x,z] of pg){const lx=x-Q.cx,lz=z-Q.cz;sommet(x,A*x+Bp*z+Cp,z,-A/nl,1/nl,-Bp/nl,rc,shade,2,(lx*tx+lz*tz)/1.6*ech,-(lx*dx+lz*dz)*kk/2.05*ech,lx*Q.nx+lz*Q.nz,lx*Q.ex+lz*Q.ez,sd,forme,Math.min(255,Math.round(Q.hw*4)),Math.min(255,Math.round(Q.hl*4)));}
        for(const [p0,p1,p2] of tris){const cy=(pg[p1][1]-pg[p0][1])*(pg[p2][0]-pg[p0][0])-(pg[p1][0]-pg[p0][0])*(pg[p2][1]-pg[p0][1]);cy>0?I.push(r0+p0,r0+p1,r0+p2):I.push(r0+p0,r0+p2,r0+p1);}
      }
      // paroi verticale sans fenêtres (bord du toit, cheminée), tournée vers l'extérieur par rapport au point (ox, oz)
      const paroi=(ax,az,bx,bz,yaB,ybB,yaT,ybT,ox,oz,c,k)=>{
        let ex2=bx-ax,ez2=bz-az;const L=Math.hypot(ex2,ez2);if(L<1e-4)return;
        if(-ez2*((ax+bx)/2-ox)+ex2*((az+bz)/2-oz)<0){[ax,az,bx,bz,yaB,ybB,yaT,ybT]=[bx,bz,ax,az,ybB,yaB,ybT,yaT];ex2=-ex2;ez2=-ez2;}
        const nx2=-ez2/L,nz2=ex2/L,s0=sommet(ax,yaB,az,nx2,0,nz2,c,k,0,0,5,0,0,0,0,0,0);
        sommet(bx,ybB,bz,nx2,0,nz2,c,k,0,0,5,0,0,0,0,0,0);sommet(bx,ybT,bz,nx2,0,nz2,c,k,0,0,5,0,0,0,0,0,0);sommet(ax,yaT,az,nx2,0,nz2,c,k,0,0,5,0,0,0,0,0,0);
        I.push(s0,s0+1,s0+2,s0,s0+2,s0+3);
      };
      // épaisseur du toit le long du débord (tuiles de rive), coupée là où le toit change de pan
      if(poly.length===4&&poly!==null&&aireP/(4*Q.hl*Q.hw)>.88){
        const ec=rc.clone().multiplyScalar(.55);
        for(let i=0;i<4;i++){const [ax,az]=poly[i],[bx,bz]=poly[(i+1)%4],ts=[0,1];
          for(let k=0;k<plans.length;k++)for(let q=k+1;q<plans.length;q++){const A=plans[k][0]-plans[q][0],Bq=plans[k][1]-plans[q][1],Cq=plans[k][2]-plans[q][2],g0=A*ax+Bq*az+Cq,g1=A*bx+Bq*bz+Cq;if(g0*g1<0)ts.push(g0/(g0-g1));}
          ts.sort((p,q)=>p-q);
          for(let k=0;k<ts.length-1;k++){const xa=ax+(bx-ax)*ts[k],za=az+(bz-az)*ts[k],xb=ax+(bx-ax)*ts[k+1],zb=az+(bz-az)*ts[k+1],ya=hTop(xa,za),yb=hTop(xb,zb);
            paroi(xa,za,xb,zb,ya-.2,yb-.2,ya,yb,Q.cx,Q.cz,ec,1);}}
      }
      // cheminée enduite sur la plupart des maisons et des immeubles à toit en pente
      if((st===1&&r()<.7)||(st===2&&r()<.9)){
        const v0=(r()*2-1)*Q.hl*.55,u0=(r()*2-1)*Q.hw*.35,ccx=Q.cx+Q.ex*v0+Q.nx*u0,ccz=Q.cz+Q.ez*v0+Q.nz*u0,w=.28+r()*.14;
        if(dansPoly(ccx,ccz,xs,zs)){
          const co=[[1,1],[-1,1],[-1,-1],[1,-1]].map(([a2,b2])=>[ccx+Q.ex*w*a2+Q.nx*w*b2,ccz+Q.ez*w*a2+Q.nz*w*b2]);
          let yb=1e9,ym=-1e9;for(const [x,z] of co)yb=Math.min(yb,hTop(x,z));for(const [x,z] of poly)ym=Math.max(ym,hTop(x,z));ym=Math.max(ym,hTop(Q.cx,Q.cz));
          const yt=Math.max(ym,yb)+.6+r()*.5,cc=wc.clone();
          for(let i=0;i<4;i++){const [ax,az]=co[i],[bx,bz]=co[(i+1)%4];paroi(ax,az,bx,bz,yb-.2,yb-.2,yt,yt,ccx,ccz,cc,shade*.95);}
          const t0=v;for(const [x,z] of co)sommet(x,yt,z,0,1,0,cc,shade*.55,0,0,5,0,0,0,0,0,0);
          const cy=(co[1][1]-co[0][1])*(co[2][0]-co[0][0])-(co[1][0]-co[0][0])*(co[2][1]-co[0][1]);
          cy>0?I.push(t0,t0+1,t0+2,t0,t0+2,t0+3):I.push(t0,t0+2,t0+1,t0,t0+3,t0+2);
        }
      }
    };
    for(let kb=0;kb<liste.length;kb++){const nI=I.length;try{unBat(liste[kb],kb);}catch(e){I.length=nI;}}
    return {pos:new Float32Array(P),nor:new Float32Array(N),col:new Uint8Array(C),toit:new Uint8Array(TT),fa:new Float32Array(FA),fb:new Uint8Array(FB),
      idx:v>65535?new Uint32Array(I):new Uint16Array(I)};
}
// version légère d'un carré, pour les bâtiments vus de loin : des boîtes à toit plat, avec les mêmes couleurs de murs
function construireSimple(liste,ph){
  let NV=0;for(const b of liste)NV+=5*(b.length-BH)/2;
  const pos=new Float32Array(NV*3),nor=new Float32Array(NV*3),col=new Uint8Array(NV*3),toit=new Uint8Array(NV),idx=[],c=new THREE.Color();let v=0;
  const coul=(i,k)=>{col[i*3]=Math.min(255,c.r*255*k);col[i*3+1]=Math.min(255,c.g*255*k);col[i*3+2]=Math.min(255,c.b*255*k);};
  for(let kb=0;kb<liste.length;kb++){
    const b=liste[kb],v0=v,nI=idx.length;
    try{
      const r=aleaBat(b,BH),bot=b[0],top=(b[1]+b[2])/2,genre=GENRES[b[3]],n=(b.length-BH)/2,info=ph&&ph[kb];
      const xs=[],zs=[];for(let i=0;i<n;i++){xs.push(b[BH+2*i]);zs.push(b[BH+1+2*i]);}
      let a=0;for(let i=0;i<n;i++){const j=(i+1)%n;a+=xs[i]*zs[j]-xs[j]*zs[i];}
      if(a>0){xs.reverse();zs.reverse();}
      const oc=osm(b,iC),oct=osm(b,iCT),shade=.92+r()*.14;
      let wc=oc||couleurMur(genre,iM>=0?b[iM]:0,r);
      if(!oc&&info&&info.mur)wc=murPhoto(info.mur,wc);
      typeof wc==='string'?c.set(wc):c.copy(wc);
      for(let i=0;i<n;i++){const j=(i+1)%n,ex=xs[j]-xs[i],ez=zs[j]-zs[i],L=Math.hypot(ex,ez)||1,nx=-ez/L,nz=ex/L;
        const q=[[xs[i],bot,zs[i]],[xs[j],bot,zs[j]],[xs[j],top,zs[j]],[xs[i],top,zs[i]]];
        for(let k=0;k<4;k++){pos.set(q[k],(v+k)*3);nor[(v+k)*3]=nx;nor[(v+k)*3+2]=nz;coul(v+k,shade*1.085);}   // même teinte que les murs détaillés vus de loin
        idx.push(v,v+1,v+2,v,v+2,v+3);v+=4;}
      if(oct)c.copy(oct).convertSRGBToLinear();
      else if(info&&info.toit)c.setRGB(info.toit[0]/255,info.toit[1]/255,info.toit[2]/255).convertSRGBToLinear();
      else c.set(couleurToit(genre,iT>=0?b[iT]:0,r)).convertSRGBToLinear();
      const r0=v;for(let i=0;i<n;i++){pos.set([xs[i],top,zs[i]],v*3);nor[v*3+1]=1;coul(v,shade);toit[v]=1;v++;}
      const tris=THREE.ShapeUtils.triangulateShape(xs.map((x,i)=>new THREE.Vector2(x,zs[i])),[]);
      for(const [p0,p1,p2] of tris){const cy=(zs[p1]-zs[p0])*(xs[p2]-xs[p0])-(xs[p1]-xs[p0])*(zs[p2]-zs[p0]);cy>0?idx.push(r0+p0,r0+p1,r0+p2):idx.push(r0+p0,r0+p2,r0+p1);}
    }catch(e){v=v0;idx.length=nI;}
  }
  return {pos,nor,col,toit,idx:v>65535?new Uint32Array(idx):new Uint16Array(idx)};
}
self.ShinBat={preparer,construire,construireSimple,lirePhoto};
})();
// ---------- en arrière-plan ----------
if(typeof document==='undefined'&&typeof importScripts==='function'){
  const infos=new Map(),listes=new Map();   // par carré : couleurs lues sur la photo, liste des bâtiments (reçue une seule fois)
  self.onmessage=e=>{
    const m=e.data;
    if(m.type==='init'){ShinBat.preparer(m.cfg);return;}
    if(m.liste)listes.set(m.id,m.liste);
    const liste=listes.get(m.id);
    if(m.type==='photo'){   // photo fine du carré : on y lit les couleurs, gardées pour toutes les constructions suivantes
      try{
        if(m.photo){const oc=new OffscreenCanvas(m.photo.width,m.photo.height),g=oc.getContext('2d');g.drawImage(m.photo,0,0);
          infos.set(m.id,ShinBat.lirePhoto(liste,g.getImageData(0,0,oc.width,oc.height).data,oc.width,oc.height,m.rect));}
        else if(m.pixels)infos.set(m.id,ShinBat.lirePhoto(liste,m.pixels,m.W,m.H,m.rect));
      }catch(err){}
      if(m.photo&&m.photo.close)m.photo.close();
      self.postMessage({type:'photo',id:m.id});return;
    }
    if(m.type!=='bat')return;
    const inf=infos.get(m.id)||null,r=m.niveau?ShinBat.construire(liste,inf):ShinBat.construireSimple(liste,inf);
    self.postMessage({type:'bat',id:m.id,seq:m.seq,niveau:m.niveau,...r},Object.values(r).map(x=>x.buffer));
  };
}
