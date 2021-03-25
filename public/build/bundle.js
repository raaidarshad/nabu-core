var app=function(){"use strict";function t(){}function e(t){return t()}function n(){return Object.create(null)}function o(t){t.forEach(e)}function r(t){return"function"==typeof t}function s(t,e){return t!=t?e==e:t!==e||t&&"object"==typeof t||"function"==typeof t}function l(t,e){t.appendChild(e)}function i(t,e,n){t.insertBefore(e,n||null)}function c(t){t.parentNode.removeChild(t)}function a(t,e){for(let n=0;n<t.length;n+=1)t[n]&&t[n].d(e)}function u(t){return document.createElement(t)}function f(t){return document.createTextNode(t)}function d(){return f(" ")}function p(t,e,n,o){return t.addEventListener(e,n,o),()=>t.removeEventListener(e,n,o)}function h(t,e,n){null==n?t.removeAttribute(e):t.getAttribute(e)!==n&&t.setAttribute(e,n)}function m(t,e){for(let n=0;n<t.options.length;n+=1){const o=t.options[n];if(o.__value===e)return void(o.selected=!0)}}let g;function $(t){g=t}function w(){if(!g)throw new Error("Function called outside component initialization");return g}const b=[],v=[],x=[],y=[],k=Promise.resolve();let _=!1;function j(t){x.push(t)}let H=!1;const O=new Set;function N(){if(!H){H=!0;do{for(let t=0;t<b.length;t+=1){const e=b[t];$(e),T(e.$$)}for($(null),b.length=0;v.length;)v.pop()();for(let t=0;t<x.length;t+=1){const e=x[t];O.has(e)||(O.add(e),e())}x.length=0}while(b.length);for(;y.length;)y.pop()();_=!1,H=!1,O.clear()}}function T(t){if(null!==t.fragment){t.update(),o(t.before_update);const e=t.dirty;t.dirty=[-1],t.fragment&&t.fragment.p(t.ctx,e),t.after_update.forEach(j)}}const E=new Set;let S;function C(){S={r:0,c:[],p:S}}function q(){S.r||o(S.c),S=S.p}function L(t,e){t&&t.i&&(E.delete(t),t.i(e))}function A(t,e,n,o){if(t&&t.o){if(E.has(t))return;E.add(t),S.c.push((()=>{E.delete(t),o&&(n&&t.d(1),o())})),t.o(e)}}function B(t,e){const n=e.token={};function o(t,o,r,s){if(e.token!==n)return;e.resolved=s;let l=e.ctx;void 0!==r&&(l=l.slice(),l[r]=s);const i=t&&(e.current=t)(l);let c=!1;e.block&&(e.blocks?e.blocks.forEach(((t,n)=>{n!==o&&t&&(C(),A(t,1,1,(()=>{e.blocks[n]===t&&(e.blocks[n]=null)})),q())})):e.block.d(1),i.c(),L(i,1),i.m(e.mount(),e.anchor),c=!0),e.block=i,e.blocks&&(e.blocks[o]=i),c&&N()}if((r=t)&&"object"==typeof r&&"function"==typeof r.then){const n=w();if(t.then((t=>{$(n),o(e.then,1,e.value,t),$(null)}),(t=>{if($(n),o(e.catch,2,e.error,t),$(null),!e.hasCatch)throw t})),e.current!==e.pending)return o(e.pending,0),!0}else{if(e.current!==e.then)return o(e.then,1,e.value,t),!0;e.resolved=t}var r}function I(t){t&&t.c()}function P(t,n,s,l){const{fragment:i,on_mount:c,on_destroy:a,after_update:u}=t.$$;i&&i.m(n,s),l||j((()=>{const n=c.map(e).filter(r);a?a.push(...n):o(n),t.$$.on_mount=[]})),u.forEach(j)}function R(t,e){const n=t.$$;null!==n.fragment&&(o(n.on_destroy),n.fragment&&n.fragment.d(e),n.on_destroy=n.fragment=null,n.ctx=[])}function z(t,e){-1===t.$$.dirty[0]&&(b.push(t),_||(_=!0,k.then(N)),t.$$.dirty.fill(0)),t.$$.dirty[e/31|0]|=1<<e%31}function M(e,r,s,l,i,a,u=[-1]){const f=g;$(e);const d=e.$$={fragment:null,ctx:null,props:a,update:t,not_equal:i,bound:n(),on_mount:[],on_destroy:[],on_disconnect:[],before_update:[],after_update:[],context:new Map(f?f.$$.context:[]),callbacks:n(),dirty:u,skip_bound:!1};let p=!1;if(d.ctx=s?s(e,r.props||{},((t,n,...o)=>{const r=o.length?o[0]:n;return d.ctx&&i(d.ctx[t],d.ctx[t]=r)&&(!d.skip_bound&&d.bound[t]&&d.bound[t](r),p&&z(e,t)),n})):[],d.update(),p=!0,o(d.before_update),d.fragment=!!l&&l(d.ctx),r.target){if(r.hydrate){const t=function(t){return Array.from(t.childNodes)}(r.target);d.fragment&&d.fragment.l(t),t.forEach(c)}else d.fragment&&d.fragment.c();r.intro&&L(e.$$.fragment),P(e,r.target,r.anchor,r.customElement),N()}$(f)}class W{$destroy(){R(this,1),this.$destroy=t}$on(t,e){const n=this.$$.callbacks[t]||(this.$$.callbacks[t]=[]);return n.push(e),()=>{const t=n.indexOf(e);-1!==t&&n.splice(t,1)}}$set(t){var e;this.$$set&&(e=t,0!==Object.keys(e).length)&&(this.$$.skip_bound=!0,this.$$set(t),this.$$.skip_bound=!1)}}function U(e){let n,o,r,s,a,f,p=e[0].title+"";return{c(){n=u("main"),o=u("div"),r=u("hr"),s=d(),a=u("a"),h(r,"class","svelte-1cxbwhl"),h(a,"href",f=e[0].link),h(a,"target","_blank"),h(a,"rel","noopener noreferrer")},m(t,e){i(t,n,e),l(n,o),l(o,r),l(o,s),l(o,a),a.innerHTML=p},p(t,[e]){1&e&&p!==(p=t[0].title+"")&&(a.innerHTML=p),1&e&&f!==(f=t[0].link)&&h(a,"href",f)},i:t,o:t,d(t){t&&c(n)}}}function Y(t,e,n){let{article:o}=e;return t.$$set=t=>{"article"in t&&n(0,o=t.article)},[o]}class F extends W{constructor(t){super(),M(this,t,Y,U,s,{article:0})}}function V(t,e,n){const o=t.slice();return o[8]=e[n],o}function G(t,e,n){const o=t.slice();return o[11]=e[n],o}function J(t){let e,n,o,r,s=t[11].text+"";return{c(){e=u("option"),n=f(s),o=d(),e.__value=r=t[11],e.value=e.__value},m(t,r){i(t,e,r),l(e,n),l(e,o)},p(t,o){1&o&&s!==(s=t[11].text+"")&&function(t,e){e=""+e,t.wholeText!==e&&(t.data=e)}(n,s),1&o&&r!==(r=t[11])&&(e.__value=r,e.value=e.__value)},d(t){t&&c(e)}}}function D(e){return{c:t,m:t,p:t,i:t,o:t,d:t}}function K(t){let e,n,o=t[7].entries,r=[];for(let e=0;e<o.length;e+=1)r[e]=Q(V(t,o,e));const s=t=>A(r[t],1,1,(()=>{r[t]=null}));return{c(){e=u("ul");for(let t=0;t<r.length;t+=1)r[t].c();h(e,"class","svelte-82k6xg")},m(t,o){i(t,e,o);for(let t=0;t<r.length;t+=1)r[t].m(e,null);n=!0},p(t,n){if(4&n){let l;for(o=t[7].entries,l=0;l<o.length;l+=1){const s=V(t,o,l);r[l]?(r[l].p(s,n),L(r[l],1)):(r[l]=Q(s),r[l].c(),L(r[l],1),r[l].m(e,null))}for(C(),l=o.length;l<r.length;l+=1)s(l);q()}},i(t){if(!n){for(let t=0;t<o.length;t+=1)L(r[t]);n=!0}},o(t){r=r.filter(Boolean);for(let t=0;t<r.length;t+=1)A(r[t]);n=!1},d(t){t&&c(e),a(r,t)}}}function Q(t){let e,n,o;return n=new F({props:{article:t[8]}}),{c(){e=u("li"),I(n.$$.fragment)},m(t,r){i(t,e,r),P(n,e,null),o=!0},p(t,e){const o={};4&e&&(o.article=t[8]),n.$set(o)},i(t){o||(L(n.$$.fragment,t),o=!0)},o(t){A(n.$$.fragment,t),o=!1},d(t){t&&c(e),R(n)}}}function X(e){let n;return{c(){n=u("p"),n.textContent="Waiting..."},m(t,e){i(t,n,e)},p:t,i:t,o:t,d(t){t&&c(n)}}}function Z(t){let e,n,r,s,f,g,$,w=t[0],b=[];for(let e=0;e<w.length;e+=1)b[e]=J(G(t,w,e));let v={ctx:t,current:null,token:null,hasCatch:!1,pending:X,then:K,catch:D,value:7,blocks:[,,,]};return B(s=t[2],v),{c(){e=u("main"),n=u("select");for(let t=0;t<b.length;t+=1)b[t].c();r=d(),v.block.c(),h(n,"class","svelte-82k6xg"),void 0===t[1]&&j((()=>t[4].call(n)))},m(o,s){i(o,e,s),l(e,n);for(let t=0;t<b.length;t+=1)b[t].m(n,null);m(n,t[1]),l(e,r),v.block.m(e,v.anchor=null),v.mount=()=>e,v.anchor=null,f=!0,g||($=[p(n,"change",t[4]),p(n,"change",tt)],g=!0)},p(e,[o]){if(t=e,1&o){let e;for(w=t[0],e=0;e<w.length;e+=1){const r=G(t,w,e);b[e]?b[e].p(r,o):(b[e]=J(r),b[e].c(),b[e].m(n,null))}for(;e<b.length;e+=1)b[e].d(1);b.length=w.length}if(3&o&&m(n,t[1]),v.ctx=t,4&o&&s!==(s=t[2])&&B(s,v));else{const e=t.slice();e[7]=v.resolved,v.block.p(e,o)}},i(t){f||(L(v.block),f=!0)},o(t){for(let t=0;t<3;t+=1){A(v.blocks[t])}f=!1},d(t){t&&c(e),a(b,t),v.block.d(),v.token=null,v=null,g=!1,o($)}}}async function tt(){}function et(t,e,n){let o,{rssOptions:r}=e,{limit:s=10}=e,l=r[0];return t.$$set=t=>{"rssOptions"in t&&n(0,r=t.rssOptions),"limit"in t&&n(3,s=t.limit)},t.$$.update=()=>{2&t.$$.dirty&&l.url,2&t.$$.dirty&&n(2,o=async function(t){const e=await fetch(`./feed?rssUrl=${t}&limit=${s}`),n=await e.json();if(e.ok)return n;throw new Error(n)}(l.url))},[r,l,o,s,function(){l=function(t){const e=t.querySelector(":checked")||t.options[0];return e&&e.__value}(this),n(1,l),n(0,r)}]}class nt extends W{constructor(t){super(),M(this,t,et,Z,s,{rssOptions:0,limit:3})}}function ot(e){let n,o,r,s,a,f,p,m,g,$,w,b,v,x,y,k,_,j,H,O,N,T,E,S,C,q;return w=new nt({props:{class:"farleft",rssOptions:e[4]}}),x=new nt({props:{rssOptions:e[3]}}),_=new nt({props:{rssOptions:e[2]}}),O=new nt({props:{rssOptions:e[1]}}),E=new nt({props:{rssOptions:e[0]}}),{c(){n=u("main"),o=u("h1"),o.textContent="Pop the Bubble News",r=d(),s=u("h5"),s.textContent="A simple RSS feed dashboard to quickly view the full spectrum of news in\n\t\tthe U.S.",a=d(),f=u("div"),p=u("div"),p.innerHTML='<p class="header svelte-1nfdjfp">Left</p> \n\t\t\t<p class="header svelte-1nfdjfp">Left-leaning</p> \n\t\t\t<p class="header svelte-1nfdjfp">Center</p> \n\t\t\t<p class="header svelte-1nfdjfp">Right-leaning</p> \n\t\t\t<p class="header svelte-1nfdjfp">Right</p>',m=d(),g=u("div"),$=u("div"),I(w.$$.fragment),b=d(),v=u("div"),I(x.$$.fragment),y=d(),k=u("div"),I(_.$$.fragment),j=d(),H=u("div"),I(O.$$.fragment),N=d(),T=u("div"),I(E.$$.fragment),S=d(),C=u("div"),C.innerHTML='<p>I often find myself wondering how people can live in such entirely\n\t\t\tdifferent realities. One commonly discussed idea is that of online\n\t\t\t&quot;bubbles&quot;, where we only consume news from certain sources and only\n\t\t\ttalk about it with like-minded people. These bubbles often reinforce\n\t\t\tour prior beliefs and further distance us from those in other\n\t\t\tbubbles. One small way to help bridge this gap is to simply be aware\n\t\t\tof the full spectrum of news available to us. I&#39;ve tried doing this\n\t\t\tby following a variety of accounts on Twitter, but there is so much\n\t\t\tnoise on that platform.</p> \n\t\t<p>In response, I made this super simple news dashboard. It is divided\n\t\t\tinto five columns, ranging from one end of the political spectrum to\n\t\t\tthe other (as defined by\n\t\t\t<a href="https://www.allsides.com/media-bias/media-bias-ratings">AllSides research</a>). Each lane lists the top 10 news stories from an RSS feed of that\n\t\t\tnews source, and you can click the headline to visit the source\n\t\t\tarticle to read further. You can also click on the news source name\n\t\t\t(try clicking on &quot;Vox (Home)&quot;) to select a different news source.\n\t\t\tWith this tool, you can get an idea of what news is disseminated\n\t\t\tacross the political spectrum at a quick glance. In short, you can\n\t\t\tpop the bubble.</p>',h(o,"class","svelte-1nfdjfp"),h(s,"class","svelte-1nfdjfp"),h(p,"class","lanes svelte-1nfdjfp"),h($,"class","farleft lane svelte-1nfdjfp"),h(v,"class","left lane svelte-1nfdjfp"),h(k,"class","center lane svelte-1nfdjfp"),h(H,"class","right lane svelte-1nfdjfp"),h(T,"class","farright lane svelte-1nfdjfp"),h(g,"class","lanes svelte-1nfdjfp"),h(f,"class","scrolling-wrapper svelte-1nfdjfp"),h(C,"class","about svelte-1nfdjfp"),h(n,"class","svelte-1nfdjfp")},m(t,e){i(t,n,e),l(n,o),l(n,r),l(n,s),l(n,a),l(n,f),l(f,p),l(f,m),l(f,g),l(g,$),P(w,$,null),l(g,b),l(g,v),P(x,v,null),l(g,y),l(g,k),P(_,k,null),l(g,j),l(g,H),P(O,H,null),l(g,N),l(g,T),P(E,T,null),l(n,S),l(n,C),q=!0},p:t,i(t){q||(L(w.$$.fragment,t),L(x.$$.fragment,t),L(_.$$.fragment,t),L(O.$$.fragment,t),L(E.$$.fragment,t),q=!0)},o(t){A(w.$$.fragment,t),A(x.$$.fragment,t),A(_.$$.fragment,t),A(O.$$.fragment,t),A(E.$$.fragment,t),q=!1},d(t){t&&c(n),R(w),R(x),R(_),R(O),R(E)}}}function rt(t){return[[{id:1,text:"OAN (Home)",url:"https://www.oann.com/category/newsroom/feed"},{id:2,text:"Breitbart (Home)",url:"http://feeds.feedburner.com/breitbart"},{id:3,text:"New York Post (Home)",url:"https://nypost.com/feed/"}],[{id:1,text:"Fox News (National)",url:"http://feeds.foxnews.com/foxnews/national"},{id:2,text:"Newsmax (Home)",url:"https://www.newsmax.com/rss/Newsfront/16"}],[{id:1,text:"NPR (Home)",url:"http://www.npr.org/rss/rss.php?id=1001"},{id:2,text:"Reuters (U.S.)",url:"https://www.reutersagency.com/feed/?best-regions=north-america&post_type=best"},{id:3,text:"The BBC (World)",url:"http://feeds.bbci.co.uk/news/rss.xml"}],[{id:1,text:"The New York Times (Home)",url:"https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"},{id:2,text:"The Washington Post (National)",url:"http://feeds.washingtonpost.com/rss/national?itid=lk_inline_manual_39"},{id:3,text:"The Guardian (World)",url:"https://www.theguardian.com/world/rss"}],[{id:1,text:"Jacobin (Home)",url:"https://jacobinmag.com/feed"},{id:2,text:"Vox (Home)",url:"https://www.vox.com/rss/index.xml"},{id:2,text:"BuzzfeedNews (Home)",url:"https://www.buzzfeed.com/index.xml"}]]}return new class extends W{constructor(t){super(),M(this,t,rt,ot,s,{})}}({target:document.body})}();
//# sourceMappingURL=bundle.js.map
