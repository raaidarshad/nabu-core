var app=function(){"use strict";function e(){}function t(e){return e()}function n(){return Object.create(null)}function o(e){e.forEach(t)}function s(e){return"function"==typeof e}function r(e,t){return e!=e?t==t:e!==t||e&&"object"==typeof e||"function"==typeof e}function l(e,t){e.appendChild(t)}function i(e,t,n){e.insertBefore(t,n||null)}function a(e){e.parentNode.removeChild(e)}function c(e,t){for(let n=0;n<e.length;n+=1)e[n]&&e[n].d(t)}function u(e){return document.createElement(e)}function f(e){return document.createTextNode(e)}function d(){return f(" ")}function h(e,t,n,o){return e.addEventListener(t,n,o),()=>e.removeEventListener(t,n,o)}function p(e,t,n){null==n?e.removeAttribute(t):e.getAttribute(t)!==n&&e.setAttribute(t,n)}function m(e,t){t=""+t,e.wholeText!==t&&(e.data=t)}function g(e,t,n,o){e.style.setProperty(t,n,o?"important":"")}function $(e,t){for(let n=0;n<e.options.length;n+=1){const o=e.options[n];if(o.__value===t)return void(o.selected=!0)}}let b;function v(e){b=e}function w(){if(!b)throw new Error("Function called outside component initialization");return b}const y=[],k=[],x=[],_=[],H=Promise.resolve();let j=!1;function O(e){x.push(e)}let T=!1;const N=new Set;function C(){if(!T){T=!0;do{for(let e=0;e<y.length;e+=1){const t=y[e];v(t),E(t.$$)}for(v(null),y.length=0;k.length;)k.pop()();for(let e=0;e<x.length;e+=1){const t=x[e];N.has(t)||(N.add(t),t())}x.length=0}while(y.length);for(;_.length;)_.pop()();j=!1,T=!1,N.clear()}}function E(e){if(null!==e.fragment){e.update(),o(e.before_update);const t=e.dirty;e.dirty=[-1],e.fragment&&e.fragment.p(e.ctx,t),e.after_update.forEach(O)}}const S=new Set;let q;function A(){q={r:0,c:[],p:q}}function L(){q.r||o(q.c),q=q.p}function z(e,t){e&&e.i&&(S.delete(e),e.i(t))}function I(e,t,n,o){if(e&&e.o){if(S.has(e))return;S.add(e),q.c.push((()=>{S.delete(e),o&&(n&&e.d(1),o())})),e.o(t)}}function P(e,t){const n=t.token={};function o(e,o,s,r){if(t.token!==n)return;t.resolved=r;let l=t.ctx;void 0!==s&&(l=l.slice(),l[s]=r);const i=e&&(t.current=e)(l);let a=!1;t.block&&(t.blocks?t.blocks.forEach(((e,n)=>{n!==o&&e&&(A(),I(e,1,1,(()=>{t.blocks[n]===e&&(t.blocks[n]=null)})),L())})):t.block.d(1),i.c(),z(i,1),i.m(t.mount(),t.anchor),a=!0),t.block=i,t.blocks&&(t.blocks[o]=i),a&&C()}if((s=e)&&"object"==typeof s&&"function"==typeof s.then){const n=w();if(e.then((e=>{v(n),o(t.then,1,t.value,e),v(null)}),(e=>{if(v(n),o(t.catch,2,t.error,e),v(null),!t.hasCatch)throw e})),t.current!==t.pending)return o(t.pending,0),!0}else{if(t.current!==t.then)return o(t.then,1,t.value,e),!0;t.resolved=e}var s}function B(e){e&&e.c()}function M(e,n,r,l){const{fragment:i,on_mount:a,on_destroy:c,after_update:u}=e.$$;i&&i.m(n,r),l||O((()=>{const n=a.map(t).filter(s);c?c.push(...n):o(n),e.$$.on_mount=[]})),u.forEach(O)}function R(e,t){const n=e.$$;null!==n.fragment&&(o(n.on_destroy),n.fragment&&n.fragment.d(t),n.on_destroy=n.fragment=null,n.ctx=[])}function W(e,t){-1===e.$$.dirty[0]&&(y.push(e),j||(j=!0,H.then(C)),e.$$.dirty.fill(0)),e.$$.dirty[t/31|0]|=1<<t%31}function U(t,s,r,l,i,c,u=[-1]){const f=b;v(t);const d=t.$$={fragment:null,ctx:null,props:c,update:e,not_equal:i,bound:n(),on_mount:[],on_destroy:[],on_disconnect:[],before_update:[],after_update:[],context:new Map(f?f.$$.context:[]),callbacks:n(),dirty:u,skip_bound:!1};let h=!1;if(d.ctx=r?r(t,s.props||{},((e,n,...o)=>{const s=o.length?o[0]:n;return d.ctx&&i(d.ctx[e],d.ctx[e]=s)&&(!d.skip_bound&&d.bound[e]&&d.bound[e](s),h&&W(t,e)),n})):[],d.update(),h=!0,o(d.before_update),d.fragment=!!l&&l(d.ctx),s.target){if(s.hydrate){const e=function(e){return Array.from(e.childNodes)}(s.target);d.fragment&&d.fragment.l(e),e.forEach(a)}else d.fragment&&d.fragment.c();s.intro&&z(t.$$.fragment),M(t,s.target,s.anchor,s.customElement),C()}v(f)}class Y{$destroy(){R(this,1),this.$destroy=e}$on(e,t){const n=this.$$.callbacks[e]||(this.$$.callbacks[e]=[]);return n.push(t),()=>{const e=n.indexOf(t);-1!==e&&n.splice(e,1)}}$set(e){var t;this.$$set&&(t=e,0!==Object.keys(t).length)&&(this.$$.skip_bound=!0,this.$$set(e),this.$$.skip_bound=!1)}}function F(t){let n,o,s,r,c,f,h=t[0].title+"";return{c(){n=u("main"),o=u("div"),s=u("hr"),r=d(),c=u("a"),p(s,"class","svelte-1cxbwhl"),p(c,"href",f=t[0].link),p(c,"target","_blank"),p(c,"rel","noopener noreferrer")},m(e,t){i(e,n,t),l(n,o),l(o,s),l(o,r),l(o,c),c.innerHTML=h},p(e,[t]){1&t&&h!==(h=e[0].title+"")&&(c.innerHTML=h),1&t&&f!==(f=e[0].link)&&p(c,"href",f)},i:e,o:e,d(e){e&&a(n)}}}function V(e,t,n){let{article:o}=t;return e.$$set=e=>{"article"in e&&n(0,o=e.article)},[o]}class G extends Y{constructor(e){super(),U(this,e,V,F,r,{article:0})}}function J(e,t,n){const o=e.slice();return o[10]=t[n],o}function D(e,t,n){const o=e.slice();return o[13]=t[n],o}function K(e){let t,n,o,s,r=e[13].text+"";return{c(){t=u("option"),n=f(r),o=d(),t.__value=s=e[13],t.value=t.__value},m(e,s){i(e,t,s),l(t,n),l(t,o)},p(e,o){4&o&&r!==(r=e[13].text+"")&&m(n,r),4&o&&s!==(s=e[13])&&(t.__value=s,t.value=t.__value)},d(e){e&&a(t)}}}function Q(t){return{c:e,m:e,p:e,i:e,o:e,d:e}}function X(e){let t,n,o=e[9].entries,s=[];for(let t=0;t<o.length;t+=1)s[t]=Z(J(e,o,t));const r=e=>I(s[e],1,1,(()=>{s[e]=null}));return{c(){t=u("ul");for(let e=0;e<s.length;e+=1)s[e].c();p(t,"class","svelte-14of4p1")},m(e,o){i(e,t,o);for(let e=0;e<s.length;e+=1)s[e].m(t,null);n=!0},p(e,n){if(16&n){let l;for(o=e[9].entries,l=0;l<o.length;l+=1){const r=J(e,o,l);s[l]?(s[l].p(r,n),z(s[l],1)):(s[l]=Z(r),s[l].c(),z(s[l],1),s[l].m(t,null))}for(A(),l=o.length;l<s.length;l+=1)r(l);L()}},i(e){if(!n){for(let e=0;e<o.length;e+=1)z(s[e]);n=!0}},o(e){s=s.filter(Boolean);for(let e=0;e<s.length;e+=1)I(s[e]);n=!1},d(e){e&&a(t),c(s,e)}}}function Z(e){let t,n,o;return n=new G({props:{article:e[10]}}),{c(){t=u("li"),B(n.$$.fragment)},m(e,s){i(e,t,s),M(n,t,null),o=!0},p(e,t){const o={};16&t&&(o.article=e[10]),n.$set(o)},i(e){o||(z(n.$$.fragment,e),o=!0)},o(e){I(n.$$.fragment,e),o=!1},d(e){e&&a(t),R(n)}}}function ee(t){let n;return{c(){n=u("p"),n.textContent="Waiting..."},m(e,t){i(e,n,t)},p:e,i:e,o:e,d(e){e&&a(n)}}}function te(e){let t,n,s,r,b,v,w,y,k,x,_,H=e[2],j=[];for(let t=0;t<H.length;t+=1)j[t]=K(D(e,H,t));let T={ctx:e,current:null,token:null,hasCatch:!1,pending:ee,then:X,catch:Q,value:9,blocks:[,,,]};return P(y=e[4],T),{c(){t=u("main"),n=u("p"),s=f(e[0]),r=d(),b=u("div"),v=u("select");for(let e=0;e<j.length;e+=1)j[e].c();w=d(),T.block.c(),p(n,"class","title svelte-14of4p1"),p(v,"class","svelte-14of4p1"),void 0===e[3]&&O((()=>e[6].call(v))),g(b,"background-color",e[1]),g(b,"height","100%"),p(b,"class","svelte-14of4p1"),p(t,"class","svelte-14of4p1")},m(o,a){i(o,t,a),l(t,n),l(n,s),l(t,r),l(t,b),l(b,v);for(let e=0;e<j.length;e+=1)j[e].m(v,null);$(v,e[3]),l(b,w),T.block.m(b,T.anchor=null),T.mount=()=>b,T.anchor=null,k=!0,x||(_=[h(v,"change",e[6]),h(v,"change",ne)],x=!0)},p(t,[n]){if(e=t,(!k||1&n)&&m(s,e[0]),4&n){let t;for(H=e[2],t=0;t<H.length;t+=1){const o=D(e,H,t);j[t]?j[t].p(o,n):(j[t]=K(o),j[t].c(),j[t].m(v,null))}for(;t<j.length;t+=1)j[t].d(1);j.length=H.length}if(12&n&&$(v,e[3]),T.ctx=e,16&n&&y!==(y=e[4])&&P(y,T));else{const t=e.slice();t[9]=T.resolved,T.block.p(t,n)}(!k||2&n)&&g(b,"background-color",e[1])},i(e){k||(z(T.block),k=!0)},o(e){for(let e=0;e<3;e+=1){I(T.blocks[e])}k=!1},d(e){e&&a(t),c(j,e),T.block.d(),T.token=null,T=null,x=!1,o(_)}}}async function ne(){}function oe(e,t,n){let o,{title:s}=t,{bgcolor:r="transparent"}=t,{rssOptions:l}=t,{limit:i=10}=t,a=l[0];return e.$$set=e=>{"title"in e&&n(0,s=e.title),"bgcolor"in e&&n(1,r=e.bgcolor),"rssOptions"in e&&n(2,l=e.rssOptions),"limit"in e&&n(5,i=e.limit)},e.$$.update=()=>{8&e.$$.dirty&&a.url,8&e.$$.dirty&&n(4,o=async function(e){const t=await fetch(`./feed?rssUrl=${e}&limit=${i}`),n=await t.json();if(t.ok)return n;throw new Error(n)}(a.url))},[s,r,l,a,o,i,function(){a=function(e){const t=e.querySelector(":checked")||e.options[0];return t&&t.__value}(this),n(3,a),n(2,l)}]}class se extends Y{constructor(e){super(),U(this,e,oe,te,r,{title:0,bgcolor:1,rssOptions:2,limit:5})}}function re(t){let n;return{c(){n=u("main"),n.innerHTML='<div class="svelte-fr0k8k"><h1 id="about" class="svelte-fr0k8k">About</h1> \n        <p class="svelte-fr0k8k">I often find myself wondering how people can live in such entirely\n            different realities. One commonly discussed idea is that of online\n            &quot;bubbles&quot;, where we only consume news from certain sources and only\n            talk about it with like-minded people. These bubbles often reinforce\n            our prior beliefs and further distance us from those in other\n            bubbles. One small way to help bridge this gap is to simply be aware\n            of the full spectrum of news available to us. I&#39;ve tried doing this\n            by following a variety of accounts on Twitter, but there is so much\n            noise on that platform.</p> \n        <p class="svelte-fr0k8k">In response, I made this super simple news dashboard. It is divided\n            into five columns, ranging from one end of the political spectrum to\n            the other (as defined by\n            <a href="https://www.allsides.com/media-bias/media-bias-ratings">AllSides research</a>). Each lane lists the top 10 news stories from an RSS feed of that\n            news source, and you can click the headline to visit the source\n            article to read further. You can also click on the news source name\n            (try clicking on &quot;Vox (Home)&quot;) to select a different news source.\n            With this tool, you can get an idea of what news is disseminated\n            across the political spectrum at a quick glance. In short, you can\n            pop the bubble.</p></div>'},m(e,t){i(e,n,t)},p:e,i:e,o:e,d(e){e&&a(n)}}}class le extends Y{constructor(e){super(),U(this,e,null,re,r,{})}}function ie(t){let n;return{c(){n=u("main"),n.innerHTML='<div class="svelte-jfszj"><h1 id="contact" class="svelte-jfszj">Contact</h1> \n        <p class="svelte-jfszj">I appreciate your thoughts on how to make this better and more usable. Please direct\n            all comments, questions, feature requests, and more to my email at <a href="mailto: raaid@protonmail.com">raaid@protonmail.com</a>.\n            I am actively working on this (though I intend to keep it simple) and will respond!</p></div>'},m(e,t){i(e,n,t)},p:e,i:e,o:e,d(e){e&&a(n)}}}class ae extends Y{constructor(e){super(),U(this,e,null,ie,r,{})}}function ce(t){let n;return{c(){n=u("main"),n.innerHTML='<div class="svelte-nd1dj6"><p class="svelte-nd1dj6">Pop the Bubble is a news aggregator, and as such, does not own and is not responsible for the content in any news article included on the site. \n            Content is owned/copyrighted by the individual author, contributor or news site, and should not be used without proper permission.</p> \n        <p class="svelte-nd1dj6">Copyright 2021 by Raaid Arshad</p></div>'},m(e,t){i(e,n,t)},p:e,i:e,o:e,d(e){e&&a(n)}}}class ue extends Y{constructor(e){super(),U(this,e,null,ce,r,{})}}function fe(t){let n;return{c(){n=u("main"),n.innerHTML='<div class="svelte-rfbvuw"><a class="headermargin svelte-rfbvuw" target="_blank" rel="noopener noreferrer" href="https://support.mozilla.org/en-US/kb/how-to-set-the-home-page">Make this your home page</a> \n        <a class="headermargin svelte-rfbvuw" href="#about">About</a> \n        <a href="#contact" class="svelte-rfbvuw">Contact</a></div>'},m(e,t){i(e,n,t)},p:e,i:e,o:e,d(e){e&&a(n)}}}class de extends Y{constructor(e){super(),U(this,e,null,fe,r,{})}}function he(t){let n,o,s,r,c,f,h,m,g,$,b,v,w,y,k,x,_,H,j,O,T,N,C,E,S,q,A,L,P,W,U;return s=new de({}),v=new se({props:{class:"farleft",rssOptions:t[4],title:"Left",bgcolor:"#99aeff33"}}),k=new se({props:{rssOptions:t[3],title:"Left-leaning",bgcolor:"#cce1ff33"}}),H=new se({props:{rssOptions:t[2],title:"Center"}}),T=new se({props:{rssOptions:t[1],title:"Right-leaning",bgcolor:"#ffe0e933"}}),E=new se({props:{rssOptions:t[0],title:"Right",bgcolor:"#ffadb633"}}),q=new le({}),L=new ae({}),W=new ue({}),{c(){n=u("main"),o=u("div"),B(s.$$.fragment),r=d(),c=u("h1"),c.textContent="Pop the Bubble News",f=d(),h=u("h5"),h.textContent="A simple RSS feed dashboard to quickly view the full spectrum of\n\t\t\tnews in the U.S.",m=d(),g=u("div"),$=u("div"),b=u("div"),B(v.$$.fragment),w=d(),y=u("div"),B(k.$$.fragment),x=d(),_=u("div"),B(H.$$.fragment),j=d(),O=u("div"),B(T.$$.fragment),N=d(),C=u("div"),B(E.$$.fragment),S=d(),B(q.$$.fragment),A=d(),B(L.$$.fragment),P=d(),B(W.$$.fragment),p(c,"class","svelte-vyga5s"),p(h,"class","svelte-vyga5s"),p(b,"class","lane svelte-vyga5s"),p(y,"class","lane svelte-vyga5s"),p(_,"class","lane svelte-vyga5s"),p(O,"class","lane svelte-vyga5s"),p(C,"class","lane svelte-vyga5s"),p($,"class","lanes svelte-vyga5s"),p(g,"class","scrolling-wrapper svelte-vyga5s"),p(o,"class","maincontent svelte-vyga5s"),p(n,"class","svelte-vyga5s")},m(e,t){i(e,n,t),l(n,o),M(s,o,null),l(o,r),l(o,c),l(o,f),l(o,h),l(o,m),l(o,g),l(g,$),l($,b),M(v,b,null),l($,w),l($,y),M(k,y,null),l($,x),l($,_),M(H,_,null),l($,j),l($,O),M(T,O,null),l($,N),l($,C),M(E,C,null),l(n,S),M(q,n,null),l(n,A),M(L,n,null),l(n,P),M(W,n,null),U=!0},p:e,i(e){U||(z(s.$$.fragment,e),z(v.$$.fragment,e),z(k.$$.fragment,e),z(H.$$.fragment,e),z(T.$$.fragment,e),z(E.$$.fragment,e),z(q.$$.fragment,e),z(L.$$.fragment,e),z(W.$$.fragment,e),U=!0)},o(e){I(s.$$.fragment,e),I(v.$$.fragment,e),I(k.$$.fragment,e),I(H.$$.fragment,e),I(T.$$.fragment,e),I(E.$$.fragment,e),I(q.$$.fragment,e),I(L.$$.fragment,e),I(W.$$.fragment,e),U=!1},d(e){e&&a(n),R(s),R(v),R(k),R(H),R(T),R(E),R(q),R(L),R(W)}}}function pe(e){return[[{id:1,text:"OAN (Home)",url:"https://www.oann.com/category/newsroom/feed"},{id:2,text:"Breitbart (Home)",url:"http://feeds.feedburner.com/breitbart"},{id:3,text:"New York Post (Home)",url:"https://nypost.com/feed/"}],[{id:1,text:"Fox News (National)",url:"http://feeds.foxnews.com/foxnews/national"},{id:2,text:"Newsmax (Home)",url:"https://www.newsmax.com/rss/Newsfront/16"}],[{id:1,text:"NPR (Home)",url:"http://www.npr.org/rss/rss.php?id=1001"},{id:2,text:"Reuters (U.S.)",url:"https://www.reutersagency.com/feed/?best-regions=north-america&post_type=best"},{id:3,text:"The BBC (World)",url:"http://feeds.bbci.co.uk/news/rss.xml"}],[{id:1,text:"The New York Times (Home)",url:"https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"},{id:2,text:"The Washington Post (National)",url:"http://feeds.washingtonpost.com/rss/national?itid=lk_inline_manual_39"},{id:3,text:"The Guardian (World)",url:"https://www.theguardian.com/world/rss"}],[{id:1,text:"Jacobin (Home)",url:"https://jacobinmag.com/feed"},{id:2,text:"Vox (Home)",url:"https://www.vox.com/rss/index.xml"},{id:2,text:"BuzzfeedNews (Home)",url:"https://www.buzzfeed.com/index.xml"}]]}return new class extends Y{constructor(e){super(),U(this,e,pe,he,r,{})}}({target:document.body})}();
//# sourceMappingURL=bundle.js.map
