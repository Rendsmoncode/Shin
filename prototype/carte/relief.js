// Relief détaillé (2 et 4 m) et routes, rivières et murs de soutènement posés dessus, pour la carte d'Aubagne.
// Ce fichier sert deux fois : chargé par la page (secours) et lancé en arrière-plan (« worker ») pour que la carte
// reste fluide quand on se déplace : la page ne fait plus qu'afficher ce qui est prêt. Il ne touche ni à la scène ni à la page.
(function(){
let C=null;   // réglages venus de la page : TU, FN, X0, Z0, GW, GD, CL, LARG, YOFF, COLS, EAU
function config(c){C=c;}
// altitude sur une grille régulière, avec les mêmes triangles que le maillage 3D
function triR(get,u,v,nu,nv){
  u=Math.min(nu-1e-6,Math.max(0,u));v=Math.min(nv-1e-6,Math.max(0,v));
  const c=u|0,r=v|0,fu=u-c,fv=v-r,a=get(c,r),b=get(c,r+1),d=get(c+1,r);
  if(fu+fv<=1)return a+(d-a)*fu+(b-a)*fv;
  const e=get(c+1,r+1);return e+(b-e)*(1-fu)+(d-e)*(1-fv);
}
const lecteur=(F,k)=>{const s=k/2,FN=C.FN;return (c,r)=>F[(1+r*s)*FN+1+c*s];};
const hauteurFine=(F,x0,z0,k)=>{const get=lecteur(F,k),n=C.TU/k;return (x,z)=>triR(get,(x-x0)/k,(z-z0)/k,n,n);};
const roche=ny=>{const t=Math.min(1,Math.max(0,(.8-ny)/.18));return t*t*(3-2*t);};
// tour du carré, dans le même ordre que la page (jupe qui cache les fentes entre deux carrés)
function tourCarre(n){
  const N1=n+1,ring=[];
  for(let c=0;c<n;c++)ring.push(c);for(let r=0;r<n;r++)ring.push(r*N1+n);for(let c=n;c>0;c--)ring.push(n*N1+c);for(let r=n;r>0;r--)ring.push(r*N1);
  return ring;
}
// maillage du sol d'un carré au pas k (2 ou 4 m) : positions, normales, coordonnées de la carte peinte, pente (roche)
function geoFin(F,x0,z0,k){
  const FN=C.FN,n=C.TU/k,N1=n+1,ring=tourCarre(n),nv=N1*N1+ring.length,fs=k/2;
  const pos=new Float32Array(nv*3),nor=new Float32Array(nv*3),uv=new Float32Array(nv*2),rk=new Float32Array(nv);
  let v=0;
  for(let r=0;r<=n;r++)for(let c=0;c<=n;c++,v++){
    const x=x0+c*k,z=z0+r*k,o=(1+r*fs)*FN+1+c*fs,dx=(F[o+1]-F[o-1])/4,dz=(F[o+FN]-F[o-FN])/4,l=Math.hypot(dx,1,dz);
    pos[v*3]=x;pos[v*3+1]=F[o];pos[v*3+2]=z;nor[v*3]=-dx/l;nor[v*3+1]=1/l;nor[v*3+2]=-dz/l;
    uv[v*2]=(x-C.X0)/C.GW;uv[v*2+1]=1-(z-C.Z0)/C.GD;rk[v]=roche(1/l);
  }
  const jupe=k*1.5+3;
  for(const s of ring){pos[v*3]=pos[s*3];pos[v*3+1]=pos[s*3+1]-jupe;pos[v*3+2]=pos[s*3+2];for(let q=0;q<3;q++)nor[v*3+q]=nor[s*3+q];uv[v*2]=uv[s*2];uv[v*2+1]=uv[s*2+1];rk[v]=rk[s];v++;}
  return {pos,nor,uv,rk};
}
function densifier(f,k){const P=[];for(let i=0;i+3<f.length;i+=2){const ax=f[i],az=f[i+1],bx=f[i+2],bz=f[i+3],n=Math.max(1,Math.ceil(Math.hypot(bx-ax,bz-az)/k));for(let q=0;q<n;q++)P.push(ax+(bx-ax)*q/n,az+(bz-az)*q/n);}P.push(f[f.length-2],f[f.length-1]);return P;}
function normale(P,i){const m=P.length/2,pi=Math.max(0,i-1),ni=Math.min(m-1,i+1);let dx=P[2*ni]-P[2*pi],dz=P[2*ni+1]-P[2*pi+1];const l=Math.hypot(dx,dz)||1;return [-dz/l,dx/l];}
function bande(P,w,yf,col,out){
  const m=P.length/2;if(m<2)return;const base=out.pos.length/3;
  for(let i=0;i<m;i++){const x=P[2*i],z=P[2*i+1],[px,pz]=normale(P,i),nx=px*w/2,nz=pz*w/2,y=yf(i,x,z,nx,nz);
    out.pos.push(x+nx,y,z+nz,x-nx,y,z-nz);out.col.push(col[0],col[1],col[2],col[0],col[1],col[2]);}
  for(let i=0;i<m-1;i++){const a=base+2*i;out.idx.push(a,a+2,a+1,a+1,a+2,a+3);}
}
function volume(P,hw,YH,YB,out){   // mur : faces des deux côtés et dessus
  const m=P.length/2;if(m<2)return;const NN=[],S=[0];
  for(let i=0;i<m;i++){NN.push(normale(P,i));if(i)S.push(S[i-1]+Math.hypot(P[2*i]-P[2*i-2],P[2*i+1]-P[2*i-1]));}
  for(const sd of [1,-1]){const b0=out.pos.length/3;
    for(let i=0;i<m;i++){const [nx,nz]=NN[i],x=P[2*i]+nx*hw*sd,z=P[2*i+1]+nz*hw*sd;
      out.pos.push(x,YH[i],z,x,YB[i],z);out.nor.push(nx*sd,0,nz*sd,nx*sd,0,nz*sd);out.uv.push(S[i]/2.5,YH[i]/2.5,S[i]/2.5,YB[i]/2.5);}
    for(let i=0;i<m-1;i++){const a=b0+2*i;sd>0?out.idx.push(a,a+1,a+2,a+1,a+3,a+2):out.idx.push(a,a+2,a+1,a+1,a+2,a+3);}}
  const b0=out.pos.length/3;
  for(let i=0;i<m;i++){const [nx,nz]=NN[i];for(const sd of [1,-1]){out.pos.push(P[2*i]+nx*hw*sd,YH[i],P[2*i+1]+nz*hw*sd);out.nor.push(0,1,0);out.uv.push(S[i]/2.5,sd*.12);}}
  for(let i=0;i<m-1;i++){const a=b0+2*i;out.idx.push(a,a+2,a+1,a+1,a+2,a+3);}
}
// routes, rivières (rubans posés sur le relief affiché) et murs de soutènement (pierre, du pied à la tête du ressaut)
function extras(F,x0,z0,k,routes,rivieres,murs){
  const h=hauteurFine(F,x0,z0,k),out={pos:[],col:[],idx:[]};
  for(const [w,f] of rivieres)bande(densifier(f,k),w,(i,x,z)=>h(x,z)+.3,C.EAU,out);
  for(const [ci,f] of routes){const cl=C.CL[ci],w=C.LARG[cl],yo=C.YOFF[cl];
    bande(densifier(f,k),w,(i,x,z,nx,nz)=>{let y=Math.max(h(x,z),h(x+nx,z+nz),h(x-nx,z-nz));if(w>8)y=Math.max(y,h(x+nx/2,z+nz/2),h(x-nx/2,z-nz/2));return y+yo;},C.COLS[cl],out);}
  const mu={pos:[],nor:[],uv:[],idx:[]},km=Math.min(k,2);
  for(const f of murs){const P=densifier(f,km),m=P.length/2,YH=[],YB=[];
    for(let i=0;i<m;i++){const x=P[2*i],z=P[2*i+1],[nx,nz]=normale(P,i),a=h(x+nx*3,z+nz*3),b=h(x-nx*3,z-nz*3),c=h(x,z);
      YH.push(Math.max(a,b,c)+.35);YB.push(Math.min(a,b,c)-.6);}
    volume(P,.3,YH,YB,mu);}
  return {rub:{pos:new Float32Array(out.pos),col:new Float32Array(out.col),idx:new Uint32Array(out.idx)},
    mur:{pos:new Float32Array(mu.pos),nor:new Float32Array(mu.nor),uv:new Float32Array(mu.uv),idx:new Uint32Array(mu.idx)}};
}
// tout ce qu'il faut pour un carré, aux deux niveaux fins (2 et 4 m)
function preparerCarre(F,x0,z0,routes,rivieres,murs){
  const g=[],ex=[];for(const k of C.pas){g.push(geoFin(F,x0,z0,k));ex.push(extras(F,x0,z0,k,routes,rivieres,murs));}
  return {g,ex};
}
self.ShinRelief={config,preparerCarre,geoFin,extras};
})();
// ---------- en arrière-plan ----------
if(typeof document==='undefined'&&typeof importScripts==='function'){
  self.onmessage=e=>{
    const m=e.data;
    if(m.type==='config'){ShinRelief.config(m.cfg);return;}
    if(m.type!=='carre')return;
    const d=ShinRelief.preparerCarre(m.F,m.x0,m.z0,m.routes,m.rivieres,m.murs),tr=[];
    for(const g of d.g)tr.push(g.pos.buffer,g.nor.buffer,g.uv.buffer,g.rk.buffer);
    for(const x of d.ex)tr.push(x.rub.pos.buffer,x.rub.col.buffer,x.rub.idx.buffer,x.mur.pos.buffer,x.mur.nor.buffer,x.mur.uv.buffer,x.mur.idx.buffer);
    self.postMessage({type:'carre',id:m.id,seq:m.seq,...d},tr);
  };
}
