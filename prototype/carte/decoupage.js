// Découpage d'Aubagne en petits quartiers, un secteur par joueur (tâche 243, règles dans docs/REGLES.md, « Le nouveau cadre »).
// - chaque joueur a son secteur, autour de son quartier de départ : personne ne se marche dessus ;
// - chaque secteur a le même nombre de quartiers (55) et chaque quartier donne 100 soldats,
//   donc tout le monde a le même nombre de soldats aux grands moments de l'histoire ;
// - les quartiers sont numérotés de 1 (le départ) à 55 en s'éloignant : chaque quartier touche un quartier
//   de numéro plus petit, donc on avance toujours de proche en proche ; l'adversaire est plus fort quand le numéro monte.
(function(root){
const PAR_JOUEUR=55, SOLDATS=100, MAX_POINTS=9000;

// Les grands moments : quand les trois joueurs ont ce nombre de quartiers, l'histoire peut avancer (CHRONOLOGIE.md).
const PORTES=[
  {n:5, titre:'Attila, à trois'},
  {n:10,titre:'La triade'},
  {n:15,titre:'La 1ʳᵉ guerre'},
  {n:20,titre:'La 2ᵉ guerre et les sauveurs'},
  {n:35,titre:'La 3ᵉ guerre'},
  {n:50,titre:'La 4ᵉ guerre'},
  {n:55,titre:'La vengeance contre la triade'},
];
// Les tyrans (les mêmes pour les trois joueurs), placés sur un numéro de quartier, avec leur difficulté.
const TYRANS={12:['Dong Zhuo',4],14:['Hernán Cortés',5],15:['Francisco Pizarro',5],
  17:['Sylla',6],19:['Cao Cao',6],20:['Basile II',6],
  25:['Bai Qi',7],30:['Hulagu',7],35:['Oda Nobunaga',7],
  38:['Tamerlan',8],42:['Xerxès',8],46:['Charlemagne',8],50:['Jules César',8],
  51:['Alexandre le Grand',9],52:['Gengis Khan',9],53:['Napoléon',9],54:['Staline',9],55:['Hitler',9]};
const ENNEMI_PERSO={Ayoub:'Kyou',Mathieu:'le colonel Morgan',Nico:'le Comte'};

function difficulte(r){return r<=4?1:r<=10?2:r<=15?3:r<=20?4:r<=27?5:r<=35?6:r<=50?7:8;}
function rarete(d){return d<=2?'commun':d<=4?'rare':d<=6?'épique':'légendaire';}
const arrondi=v=>Math.max(50,Math.round(v/10)*10);

// L'adversaire qui tient le quartier n° r du secteur du joueur.
function adversaire(r,joueur){
  const avant=(r-1)*SOLDATS;   // soldats du joueur quand il attaque ce quartier
  if(r===1)return null;
  if(r===2)return {nom:'Ray Dark',type:'fiction',diff:1,soldats:60,texte:'le premier adversaire, le même pour tout le monde'};
  if(r===5)return {nom:ENNEMI_PERSO[joueur]||'son propre ennemi',type:'ennemi',diff:2,soldats:500,texte:'trop fort la première fois (défaite prévue), battu après le tutoriel'};
  if(TYRANS[r])return {nom:TYRANS[r][0],type:'tyran',diff:TYRANS[r][1],soldats:arrondi(avant*1.1),texte:'tyran'};
  const d=difficulte(r);
  return {nom:'un personnage du gacha',type:'gacha',diff:d,rarete:rarete(d),soldats:arrondi(avant*0.7),texte:'personnage '+rarete(d)};
}
// Le grand moment à passer avant de pouvoir attaquer le quartier n° r (ou null).
function porteAvant(r){return PORTES.find(p=>p.n===r-1)||null;}

// petit tirage au hasard reproductible (même découpage à chaque chargement)
function hasard(seed){return()=>{seed|=0;seed=seed+0x6D2B79F5|0;let x=Math.imul(seed^seed>>>15,1|seed);x=x+Math.imul(x^x>>>7,61|x)^x;return((x^x>>>14)>>>0)/4294967296;};}

// pts : positions des bâtiments [[x,z]…] (là où vivent les futurs soldats) ; departs : [[x,z]…] un par joueur.
// Rend {centres, secteur, rang, del} : le centre de chaque quartier, son joueur (indice), son numéro (1 à K), la triangulation.
function decouper(pts,departs,Delaunay,K=PAR_JOUEUR){
  const J=departs.length;
  let P=pts;
  if(P.length>MAX_POINTS){const s=P.length/MAX_POINTS;P=[];for(let i=0;i<MAX_POINTS;i++)P.push(pts[Math.floor(i*s)]);}
  if(P.length<J*K*3)return null;
  const N=P.length,dist=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);

  // 1. trois secteurs avec autant de bâtiments chacun (on pousse la frontière du secteur trop gros)
  const D=P.map(p=>departs.map(s=>dist(p,s))),sect=new Int32Array(N),w=new Float64Array(J);
  let pas=1500;
  for(let it=0;it<300;it++){
    const cnt=new Array(J).fill(0);
    for(let i=0;i<N;i++){let b=0,bv=Infinity;for(let j=0;j<J;j++){const v=D[i][j]+w[j];if(v<bv){bv=v;b=j;}}sect[i]=b;cnt[b]++;}
    let ok=true;
    for(let j=0;j<J;j++){const e=cnt[j]/N-1/J;if(Math.abs(e)>0.003)ok=false;w[j]+=pas*e*J;}
    if(ok)break;pas*=0.98;
  }

  // 2. dans chaque secteur, K quartiers qui regroupent à peu près autant de bâtiments (k-moyennes)
  const R=hasard(243),centres=[],secteur=[];
  for(let j=0;j<J;j++){
    const Q=[];for(let i=0;i<N;i++)if(sect[i]===j)Q.push(P[i]);
    // premier centre au plus près du départ, les suivants tirés loin des centres déjà posés (k-moyennes++)
    let best=0;Q.forEach((p,i)=>{if(dist(p,departs[j])<dist(Q[best],departs[j]))best=i;});
    const C=[Q[best].slice()],dm=Q.map(p=>dist(p,C[0])**2);
    while(C.length<K){let tot=0;for(const v of dm)tot+=v;let t=R()*tot,i=0;while(i<Q.length-1&&(t-=dm[i])>0)i++;
      C.push(Q[i].slice());for(let q=0;q<Q.length;q++)dm[q]=Math.min(dm[q],dist(Q[q],C[C.length-1])**2);}
    const lab=new Int32Array(Q.length);
    for(let it=0;it<25;it++){
      for(let q=0;q<Q.length;q++){let b=0,bv=Infinity;for(let k=0;k<K;k++){const v=(Q[q][0]-C[k][0])**2+(Q[q][1]-C[k][1])**2;if(v<bv){bv=v;b=k;}}lab[q]=b;}
      const sx=new Float64Array(K),sz=new Float64Array(K),n=new Int32Array(K);
      for(let q=0;q<Q.length;q++){sx[lab[q]]+=Q[q][0];sz[lab[q]]+=Q[q][1];n[lab[q]]++;}
      for(let k=0;k<K;k++)if(n[k])C[k]=[sx[k]/n[k],sz[k]/n[k]];
      else{let f=0,fv=-1;for(let q=0;q<Q.length;q++){const v=dist(Q[q],C[lab[q]]);if(v>fv){fv=v;f=q;}}C[k]=Q[f].slice();}
    }
    for(const c of C){centres.push(c);secteur.push(j);}
  }

  // 3. numéros : du départ vers l'extérieur, chaque quartier touche un quartier déjà numéroté (de proche en proche)
  const del=Delaunay.from(centres),rang=new Array(centres.length).fill(0);
  for(let j=0;j<J;j++){
    const ids=centres.map((c,i)=>i).filter(i=>secteur[i]===j);
    let s=ids[0];for(const i of ids)if(dist(centres[i],departs[j])<dist(centres[s],departs[j]))s=i;
    const d=new Map(ids.map(i=>[i,Infinity]));d.set(s,0);
    let r=0;const fait=new Set();
    while(fait.size<ids.length){
      let u=-1,uv=Infinity;for(const i of ids)if(!fait.has(i)&&d.get(i)<uv){uv=d.get(i);u=i;}
      if(u<0){ // morceau du secteur qui ne touche pas le reste : on le prend par ordre de distance
        for(const i of ids)if(!fait.has(i)&&(u<0||dist(centres[i],departs[j])<dist(centres[u],departs[j])))u=i;
        d.set(u,1e9);}
      fait.add(u);rang[u]=++r;
      for(const v of del.neighbors(u))if(secteur[v]===j&&!fait.has(v)){const nv=d.get(u)+dist(centres[u],centres[v]);if(nv<d.get(v))d.set(v,nv);}
    }
  }
  return {centres,secteur,rang,del};
}

const api={PAR_JOUEUR,SOLDATS,PORTES,TYRANS,adversaire,porteAvant,decouper};
if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.ShinDecoupage=api;
})(this);
