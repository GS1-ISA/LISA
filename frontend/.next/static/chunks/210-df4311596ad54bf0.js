(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[210],{6435:function(t,e,s){"use strict";s.d(e,{F:function(){return l},f:function(){return c}});var i=s(2265);let a=["light","dark"],r="(prefers-color-scheme: dark)",n="undefined"==typeof window,o=(0,i.createContext)(void 0),u={setTheme:t=>{},themes:[]},l=()=>{var t;return null!==(t=(0,i.useContext)(o))&&void 0!==t?t:u},c=t=>(0,i.useContext)(o)?i.createElement(i.Fragment,null,t.children):i.createElement(d,t),h=["light","dark"],d=({forcedTheme:t,disableTransitionOnChange:e=!1,enableSystem:s=!0,enableColorScheme:n=!0,storageKey:u="theme",themes:l=h,defaultTheme:c=s?"system":"light",attribute:d="data-theme",value:g,children:v,nonce:b})=>{let[C,w]=(0,i.useState)(()=>p(u,c)),[x,O]=(0,i.useState)(()=>p(u)),S=g?Object.values(g):l,q=(0,i.useCallback)(t=>{let i=t;if(!i)return;"system"===t&&s&&(i=y());let r=g?g[i]:i,o=e?m():null,u=document.documentElement;if("class"===d?(u.classList.remove(...S),r&&u.classList.add(r)):r?u.setAttribute(d,r):u.removeAttribute(d),n){let t=a.includes(c)?c:null,e=a.includes(i)?i:t;u.style.colorScheme=e}null==o||o()},[]),E=(0,i.useCallback)(t=>{w(t);try{localStorage.setItem(u,t)}catch(t){}},[t]),A=(0,i.useCallback)(e=>{O(y(e)),"system"===C&&s&&!t&&q("system")},[C,t]);(0,i.useEffect)(()=>{let t=window.matchMedia(r);return t.addListener(A),A(t),()=>t.removeListener(A)},[A]),(0,i.useEffect)(()=>{let t=t=>{t.key===u&&E(t.newValue||c)};return window.addEventListener("storage",t),()=>window.removeEventListener("storage",t)},[E]),(0,i.useEffect)(()=>{q(null!=t?t:C)},[t,C]);let D=(0,i.useMemo)(()=>({theme:C,setTheme:E,forcedTheme:t,resolvedTheme:"system"===C?x:C,themes:s?[...l,"system"]:l,systemTheme:s?x:void 0}),[C,E,t,x,s,l]);return i.createElement(o.Provider,{value:D},i.createElement(f,{forcedTheme:t,disableTransitionOnChange:e,enableSystem:s,enableColorScheme:n,storageKey:u,themes:l,defaultTheme:c,attribute:d,value:g,children:v,attrs:S,nonce:b}),v)},f=(0,i.memo)(({forcedTheme:t,storageKey:e,attribute:s,enableSystem:n,enableColorScheme:o,defaultTheme:u,value:l,attrs:c,nonce:h})=>{let d="system"===u,f="class"===s?`var d=document.documentElement,c=d.classList;c.remove(${c.map(t=>`'${t}'`).join(",")});`:`var d=document.documentElement,n='${s}',s='setAttribute';`,p=o?a.includes(u)&&u?`if(e==='light'||e==='dark'||!e)d.style.colorScheme=e||'${u}'`:"if(e==='light'||e==='dark')d.style.colorScheme=e":"",m=(t,e=!1,i=!0)=>{let r=l?l[t]:t,n=e?t+"|| ''":`'${r}'`,u="";return o&&i&&!e&&a.includes(t)&&(u+=`d.style.colorScheme = '${t}';`),"class"===s?u+=e||r?`c.add(${n})`:"null":r&&(u+=`d[s](n,${n})`),u},y=t?`!function(){${f}${m(t)}}()`:n?`!function(){try{${f}var e=localStorage.getItem('${e}');if('system'===e||(!e&&${d})){var t='${r}',m=window.matchMedia(t);if(m.media!==t||m.matches){${m("dark")}}else{${m("light")}}}else if(e){${l?`var x=${JSON.stringify(l)};`:""}${m(l?"x[e]":"e",!0)}}${d?"":"else{"+m(u,!1,!1)+"}"}${p}}catch(e){}}()`:`!function(){try{${f}var e=localStorage.getItem('${e}');if(e){${l?`var x=${JSON.stringify(l)};`:""}${m(l?"x[e]":"e",!0)}}else{${m(u,!1,!1)};}${p}}catch(t){}}();`;return i.createElement("script",{nonce:h,dangerouslySetInnerHTML:{__html:y}})},()=>!0),p=(t,e)=>{let s;if(!n){try{s=localStorage.getItem(t)||void 0}catch(t){}return s||e}},m=()=>{let t=document.createElement("style");return t.appendChild(document.createTextNode("*{-webkit-transition:none!important;-moz-transition:none!important;-o-transition:none!important;-ms-transition:none!important;transition:none!important}")),document.head.appendChild(t),()=>{window.getComputedStyle(document.body),setTimeout(()=>{document.head.removeChild(t)},1)}},y=t=>(t||(t=window.matchMedia(r)),t.matches?"dark":"light")},9646:function(t){t.exports={style:{fontFamily:"'__Inter_f367f3', '__Inter_Fallback_f367f3'",fontStyle:"normal"},className:"__className_f367f3"}},7470:function(t,e,s){"use strict";s.d(e,{R:function(){return o},m:function(){return n}});var i=s(7987),a=s(9024),r=s(1640),n=class extends a.F{#t;#e;#s;#i;constructor(t){super(),this.#t=t.client,this.mutationId=t.mutationId,this.#s=t.mutationCache,this.#e=[],this.state=t.state||o(),this.setOptions(t.options),this.scheduleGc()}setOptions(t){this.options=t,this.updateGcTime(this.options.gcTime)}get meta(){return this.options.meta}addObserver(t){this.#e.includes(t)||(this.#e.push(t),this.clearGcTimeout(),this.#s.notify({type:"observerAdded",mutation:this,observer:t}))}removeObserver(t){this.#e=this.#e.filter(e=>e!==t),this.scheduleGc(),this.#s.notify({type:"observerRemoved",mutation:this,observer:t})}optionalRemove(){this.#e.length||("pending"===this.state.status?this.scheduleGc():this.#s.remove(this))}continue(){return this.#i?.continue()??this.execute(this.state.variables)}async execute(t){let e=()=>{this.#a({type:"continue"})},s={client:this.#t,meta:this.options.meta,mutationKey:this.options.mutationKey};this.#i=(0,r.Mz)({fn:()=>this.options.mutationFn?this.options.mutationFn(t,s):Promise.reject(Error("No mutationFn found")),onFail:(t,e)=>{this.#a({type:"failed",failureCount:t,error:e})},onPause:()=>{this.#a({type:"pause"})},onContinue:e,retry:this.options.retry??0,retryDelay:this.options.retryDelay,networkMode:this.options.networkMode,canRun:()=>this.#s.canRun(this)});let i="pending"===this.state.status,a=!this.#i.canStart();try{if(i)e();else{this.#a({type:"pending",variables:t,isPaused:a}),await this.#s.config.onMutate?.(t,this,s);let e=await this.options.onMutate?.(t,s);e!==this.state.context&&this.#a({type:"pending",context:e,variables:t,isPaused:a})}let r=await this.#i.start();return await this.#s.config.onSuccess?.(r,t,this.state.context,this,s),await this.options.onSuccess?.(r,t,this.state.context,s),await this.#s.config.onSettled?.(r,null,this.state.variables,this.state.context,this,s),await this.options.onSettled?.(r,null,t,this.state.context,s),this.#a({type:"success",data:r}),r}catch(e){try{throw await this.#s.config.onError?.(e,t,this.state.context,this,s),await this.options.onError?.(e,t,this.state.context,s),await this.#s.config.onSettled?.(void 0,e,this.state.variables,this.state.context,this,s),await this.options.onSettled?.(void 0,e,t,this.state.context,s),e}finally{this.#a({type:"error",error:e})}}finally{this.#s.runNext(this)}}#a(t){this.state=(e=>{switch(t.type){case"failed":return{...e,failureCount:t.failureCount,failureReason:t.error};case"pause":return{...e,isPaused:!0};case"continue":return{...e,isPaused:!1};case"pending":return{...e,context:t.context,data:void 0,failureCount:0,failureReason:null,error:null,isPaused:t.isPaused,status:"pending",variables:t.variables,submittedAt:Date.now()};case"success":return{...e,data:t.data,failureCount:0,failureReason:null,error:null,status:"success",isPaused:!1};case"error":return{...e,data:void 0,error:t.error,failureCount:e.failureCount+1,failureReason:t.error,isPaused:!1,status:"error"}}})(this.state),i.Vr.batch(()=>{this.#e.forEach(e=>{e.onMutationUpdate(t)}),this.#s.notify({mutation:this,type:"updated",action:t})})}};function o(){return{context:void 0,data:void 0,error:null,failureCount:0,failureReason:null,isPaused:!1,status:"idle",variables:void 0,submittedAt:0}}},3002:function(t,e,s){"use strict";s.d(e,{A:function(){return o},z:function(){return u}});var i=s(300),a=s(7987),r=s(1640),n=s(9024),o=class extends n.F{#r;#n;#o;#t;#i;#u;#l;constructor(t){super(),this.#l=!1,this.#u=t.defaultOptions,this.setOptions(t.options),this.observers=[],this.#t=t.client,this.#o=this.#t.getQueryCache(),this.queryKey=t.queryKey,this.queryHash=t.queryHash,this.#r=l(this.options),this.state=t.state??this.#r,this.scheduleGc()}get meta(){return this.options.meta}get promise(){return this.#i?.promise}setOptions(t){if(this.options={...this.#u,...t},this.updateGcTime(this.options.gcTime),this.state&&void 0===this.state.data){let t=l(this.options);void 0!==t.data&&(this.setData(t.data,{updatedAt:t.dataUpdatedAt,manual:!0}),this.#r=t)}}optionalRemove(){this.observers.length||"idle"!==this.state.fetchStatus||this.#o.remove(this)}setData(t,e){let s=(0,i.oE)(this.state.data,t,this.options);return this.#a({data:s,type:"success",dataUpdatedAt:e?.updatedAt,manual:e?.manual}),s}setState(t,e){this.#a({type:"setState",state:t,setStateOptions:e})}cancel(t){let e=this.#i?.promise;return this.#i?.cancel(t),e?e.then(i.ZT).catch(i.ZT):Promise.resolve()}destroy(){super.destroy(),this.cancel({silent:!0})}reset(){this.destroy(),this.setState(this.#r)}isActive(){return this.observers.some(t=>!1!==(0,i.Nc)(t.options.enabled,this))}isDisabled(){return this.getObserversCount()>0?!this.isActive():this.options.queryFn===i.CN||this.state.dataUpdateCount+this.state.errorUpdateCount===0}isStatic(){return this.getObserversCount()>0&&this.observers.some(t=>"static"===(0,i.KC)(t.options.staleTime,this))}isStale(){return this.getObserversCount()>0?this.observers.some(t=>t.getCurrentResult().isStale):void 0===this.state.data||this.state.isInvalidated}isStaleByTime(t=0){return void 0===this.state.data||"static"!==t&&(!!this.state.isInvalidated||!(0,i.Kp)(this.state.dataUpdatedAt,t))}onFocus(){let t=this.observers.find(t=>t.shouldFetchOnWindowFocus());t?.refetch({cancelRefetch:!1}),this.#i?.continue()}onOnline(){let t=this.observers.find(t=>t.shouldFetchOnReconnect());t?.refetch({cancelRefetch:!1}),this.#i?.continue()}addObserver(t){this.observers.includes(t)||(this.observers.push(t),this.clearGcTimeout(),this.#o.notify({type:"observerAdded",query:this,observer:t}))}removeObserver(t){this.observers.includes(t)&&(this.observers=this.observers.filter(e=>e!==t),this.observers.length||(this.#i&&(this.#l?this.#i.cancel({revert:!0}):this.#i.cancelRetry()),this.scheduleGc()),this.#o.notify({type:"observerRemoved",query:this,observer:t}))}getObserversCount(){return this.observers.length}invalidate(){this.state.isInvalidated||this.#a({type:"invalidate"})}async fetch(t,e){if("idle"!==this.state.fetchStatus&&this.#i?.status()!=="rejected"){if(void 0!==this.state.data&&e?.cancelRefetch)this.cancel({silent:!0});else if(this.#i)return this.#i.continueRetry(),this.#i.promise}if(t&&this.setOptions(t),!this.options.queryFn){let t=this.observers.find(t=>t.options.queryFn);t&&this.setOptions(t.options)}let s=new AbortController,a=t=>{Object.defineProperty(t,"signal",{enumerable:!0,get:()=>(this.#l=!0,s.signal)})},n=()=>{let t=(0,i.cG)(this.options,e),s=(()=>{let t={client:this.#t,queryKey:this.queryKey,meta:this.meta};return a(t),t})();return(this.#l=!1,this.options.persister)?this.options.persister(t,s,this):t(s)},o=(()=>{let t={fetchOptions:e,options:this.options,queryKey:this.queryKey,client:this.#t,state:this.state,fetchFn:n};return a(t),t})();this.options.behavior?.onFetch(o,this),this.#n=this.state,("idle"===this.state.fetchStatus||this.state.fetchMeta!==o.fetchOptions?.meta)&&this.#a({type:"fetch",meta:o.fetchOptions?.meta}),this.#i=(0,r.Mz)({initialPromise:e?.initialPromise,fn:o.fetchFn,onCancel:t=>{t instanceof r.p8&&t.revert&&this.setState({...this.#n,fetchStatus:"idle"}),s.abort()},onFail:(t,e)=>{this.#a({type:"failed",failureCount:t,error:e})},onPause:()=>{this.#a({type:"pause"})},onContinue:()=>{this.#a({type:"continue"})},retry:o.options.retry,retryDelay:o.options.retryDelay,networkMode:o.options.networkMode,canRun:()=>!0});try{let t=await this.#i.start();if(void 0===t)throw Error(`${this.queryHash} data is undefined`);return this.setData(t),this.#o.config.onSuccess?.(t,this),this.#o.config.onSettled?.(t,this.state.error,this),t}catch(t){if(t instanceof r.p8){if(t.silent)return this.#i.promise;if(t.revert){if(void 0===this.state.data)throw t;return this.state.data}}throw this.#a({type:"error",error:t}),this.#o.config.onError?.(t,this),this.#o.config.onSettled?.(this.state.data,t,this),t}finally{this.scheduleGc()}}#a(t){this.state=(e=>{switch(t.type){case"failed":return{...e,fetchFailureCount:t.failureCount,fetchFailureReason:t.error};case"pause":return{...e,fetchStatus:"paused"};case"continue":return{...e,fetchStatus:"fetching"};case"fetch":return{...e,...u(e.data,this.options),fetchMeta:t.meta??null};case"success":let s={...e,data:t.data,dataUpdateCount:e.dataUpdateCount+1,dataUpdatedAt:t.dataUpdatedAt??Date.now(),error:null,isInvalidated:!1,status:"success",...!t.manual&&{fetchStatus:"idle",fetchFailureCount:0,fetchFailureReason:null}};return this.#n=t.manual?s:void 0,s;case"error":let i=t.error;return{...e,error:i,errorUpdateCount:e.errorUpdateCount+1,errorUpdatedAt:Date.now(),fetchFailureCount:e.fetchFailureCount+1,fetchFailureReason:i,fetchStatus:"idle",status:"error"};case"invalidate":return{...e,isInvalidated:!0};case"setState":return{...e,...t.state}}})(this.state),a.Vr.batch(()=>{this.observers.forEach(t=>{t.onQueryUpdate()}),this.#o.notify({query:this,type:"updated",action:t})})}};function u(t,e){return{fetchFailureCount:0,fetchFailureReason:null,fetchStatus:(0,r.Kw)(e.networkMode)?"fetching":"paused",...void 0===t&&{error:null,status:"pending"}}}function l(t){let e="function"==typeof t.initialData?t.initialData():t.initialData,s=void 0!==e,i=s?"function"==typeof t.initialDataUpdatedAt?t.initialDataUpdatedAt():t.initialDataUpdatedAt:0;return{data:e,dataUpdateCount:0,dataUpdatedAt:s?i??Date.now():0,error:null,errorUpdateCount:0,errorUpdatedAt:0,fetchFailureCount:0,fetchFailureReason:null,fetchMeta:null,isInvalidated:!1,status:s?"success":"pending",fetchStatus:"idle"}}},8908:function(t,e,s){"use strict";s.d(e,{S:function(){return m}});var i=s(300),a=s(3002),r=s(7987),n=s(2996),o=class extends n.l{constructor(t={}){super(),this.config=t,this.#c=new Map}#c;build(t,e,s){let r=e.queryKey,n=e.queryHash??(0,i.Rm)(r,e),o=this.get(n);return o||(o=new a.A({client:t,queryKey:r,queryHash:n,options:t.defaultQueryOptions(e),state:s,defaultOptions:t.getQueryDefaults(r)}),this.add(o)),o}add(t){this.#c.has(t.queryHash)||(this.#c.set(t.queryHash,t),this.notify({type:"added",query:t}))}remove(t){let e=this.#c.get(t.queryHash);e&&(t.destroy(),e===t&&this.#c.delete(t.queryHash),this.notify({type:"removed",query:t}))}clear(){r.Vr.batch(()=>{this.getAll().forEach(t=>{this.remove(t)})})}get(t){return this.#c.get(t)}getAll(){return[...this.#c.values()]}find(t){let e={exact:!0,...t};return this.getAll().find(t=>(0,i._x)(e,t))}findAll(t={}){let e=this.getAll();return Object.keys(t).length>0?e.filter(e=>(0,i._x)(t,e)):e}notify(t){r.Vr.batch(()=>{this.listeners.forEach(e=>{e(t)})})}onFocus(){r.Vr.batch(()=>{this.getAll().forEach(t=>{t.onFocus()})})}onOnline(){r.Vr.batch(()=>{this.getAll().forEach(t=>{t.onOnline()})})}},u=s(7470),l=class extends n.l{constructor(t={}){super(),this.config=t,this.#h=new Set,this.#d=new Map,this.#f=0}#h;#d;#f;build(t,e,s){let i=new u.m({client:t,mutationCache:this,mutationId:++this.#f,options:t.defaultMutationOptions(e),state:s});return this.add(i),i}add(t){this.#h.add(t);let e=c(t);if("string"==typeof e){let s=this.#d.get(e);s?s.push(t):this.#d.set(e,[t])}this.notify({type:"added",mutation:t})}remove(t){if(this.#h.delete(t)){let e=c(t);if("string"==typeof e){let s=this.#d.get(e);if(s){if(s.length>1){let e=s.indexOf(t);-1!==e&&s.splice(e,1)}else s[0]===t&&this.#d.delete(e)}}}this.notify({type:"removed",mutation:t})}canRun(t){let e=c(t);if("string"!=typeof e)return!0;{let s=this.#d.get(e),i=s?.find(t=>"pending"===t.state.status);return!i||i===t}}runNext(t){let e=c(t);if("string"!=typeof e)return Promise.resolve();{let s=this.#d.get(e)?.find(e=>e!==t&&e.state.isPaused);return s?.continue()??Promise.resolve()}}clear(){r.Vr.batch(()=>{this.#h.forEach(t=>{this.notify({type:"removed",mutation:t})}),this.#h.clear(),this.#d.clear()})}getAll(){return Array.from(this.#h)}find(t){let e={exact:!0,...t};return this.getAll().find(t=>(0,i.X7)(e,t))}findAll(t={}){return this.getAll().filter(e=>(0,i.X7)(t,e))}notify(t){r.Vr.batch(()=>{this.listeners.forEach(e=>{e(t)})})}resumePausedMutations(){let t=this.getAll().filter(t=>t.state.isPaused);return r.Vr.batch(()=>Promise.all(t.map(t=>t.continue().catch(i.ZT))))}};function c(t){return t.options.scope?.id}var h=s(9198),d=s(436);function f(t){return{onFetch:(e,s)=>{let a=e.options,r=e.fetchOptions?.meta?.fetchMore?.direction,n=e.state.data?.pages||[],o=e.state.data?.pageParams||[],u={pages:[],pageParams:[]},l=0,c=async()=>{let s=!1,c=t=>{Object.defineProperty(t,"signal",{enumerable:!0,get:()=>(e.signal.aborted?s=!0:e.signal.addEventListener("abort",()=>{s=!0}),e.signal)})},h=(0,i.cG)(e.options,e.fetchOptions),d=async(t,a,r)=>{if(s)return Promise.reject();if(null==a&&t.pages.length)return Promise.resolve(t);let n=(()=>{let t={client:e.client,queryKey:e.queryKey,pageParam:a,direction:r?"backward":"forward",meta:e.options.meta};return c(t),t})(),o=await h(n),{maxPages:u}=e.options,l=r?i.Ht:i.VX;return{pages:l(t.pages,o,u),pageParams:l(t.pageParams,a,u)}};if(r&&n.length){let t="backward"===r,e={pages:n,pageParams:o},s=(t?function(t,{pages:e,pageParams:s}){return e.length>0?t.getPreviousPageParam?.(e[0],e,s[0],s):void 0}:p)(a,e);u=await d(e,s,t)}else{let e=t??n.length;do{let t=0===l?o[0]??a.initialPageParam:p(a,u);if(l>0&&null==t)break;u=await d(u,t),l++}while(l<e)}return u};e.options.persister?e.fetchFn=()=>e.options.persister?.(c,{client:e.client,queryKey:e.queryKey,meta:e.options.meta,signal:e.signal},s):e.fetchFn=c}}}function p(t,{pages:e,pageParams:s}){let i=e.length-1;return e.length>0?t.getNextPageParam(e[i],e,s[i],s):void 0}var m=class{#p;#s;#u;#m;#y;#g;#v;#b;constructor(t={}){this.#p=t.queryCache||new o,this.#s=t.mutationCache||new l,this.#u=t.defaultOptions||{},this.#m=new Map,this.#y=new Map,this.#g=0}mount(){this.#g++,1===this.#g&&(this.#v=h.j.subscribe(async t=>{t&&(await this.resumePausedMutations(),this.#p.onFocus())}),this.#b=d.N.subscribe(async t=>{t&&(await this.resumePausedMutations(),this.#p.onOnline())}))}unmount(){this.#g--,0===this.#g&&(this.#v?.(),this.#v=void 0,this.#b?.(),this.#b=void 0)}isFetching(t){return this.#p.findAll({...t,fetchStatus:"fetching"}).length}isMutating(t){return this.#s.findAll({...t,status:"pending"}).length}getQueryData(t){let e=this.defaultQueryOptions({queryKey:t});return this.#p.get(e.queryHash)?.state.data}ensureQueryData(t){let e=this.defaultQueryOptions(t),s=this.#p.build(this,e),a=s.state.data;return void 0===a?this.fetchQuery(t):(t.revalidateIfStale&&s.isStaleByTime((0,i.KC)(e.staleTime,s))&&this.prefetchQuery(e),Promise.resolve(a))}getQueriesData(t){return this.#p.findAll(t).map(({queryKey:t,state:e})=>[t,e.data])}setQueryData(t,e,s){let a=this.defaultQueryOptions({queryKey:t}),r=this.#p.get(a.queryHash),n=r?.state.data,o=(0,i.SE)(e,n);if(void 0!==o)return this.#p.build(this,a).setData(o,{...s,manual:!0})}setQueriesData(t,e,s){return r.Vr.batch(()=>this.#p.findAll(t).map(({queryKey:t})=>[t,this.setQueryData(t,e,s)]))}getQueryState(t){let e=this.defaultQueryOptions({queryKey:t});return this.#p.get(e.queryHash)?.state}removeQueries(t){let e=this.#p;r.Vr.batch(()=>{e.findAll(t).forEach(t=>{e.remove(t)})})}resetQueries(t,e){let s=this.#p;return r.Vr.batch(()=>(s.findAll(t).forEach(t=>{t.reset()}),this.refetchQueries({type:"active",...t},e)))}cancelQueries(t,e={}){let s={revert:!0,...e};return Promise.all(r.Vr.batch(()=>this.#p.findAll(t).map(t=>t.cancel(s)))).then(i.ZT).catch(i.ZT)}invalidateQueries(t,e={}){return r.Vr.batch(()=>(this.#p.findAll(t).forEach(t=>{t.invalidate()}),t?.refetchType==="none")?Promise.resolve():this.refetchQueries({...t,type:t?.refetchType??t?.type??"active"},e))}refetchQueries(t,e={}){let s={...e,cancelRefetch:e.cancelRefetch??!0};return Promise.all(r.Vr.batch(()=>this.#p.findAll(t).filter(t=>!t.isDisabled()&&!t.isStatic()).map(t=>{let e=t.fetch(void 0,s);return s.throwOnError||(e=e.catch(i.ZT)),"paused"===t.state.fetchStatus?Promise.resolve():e}))).then(i.ZT)}fetchQuery(t){let e=this.defaultQueryOptions(t);void 0===e.retry&&(e.retry=!1);let s=this.#p.build(this,e);return s.isStaleByTime((0,i.KC)(e.staleTime,s))?s.fetch(e):Promise.resolve(s.state.data)}prefetchQuery(t){return this.fetchQuery(t).then(i.ZT).catch(i.ZT)}fetchInfiniteQuery(t){return t.behavior=f(t.pages),this.fetchQuery(t)}prefetchInfiniteQuery(t){return this.fetchInfiniteQuery(t).then(i.ZT).catch(i.ZT)}ensureInfiniteQueryData(t){return t.behavior=f(t.pages),this.ensureQueryData(t)}resumePausedMutations(){return d.N.isOnline()?this.#s.resumePausedMutations():Promise.resolve()}getQueryCache(){return this.#p}getMutationCache(){return this.#s}getDefaultOptions(){return this.#u}setDefaultOptions(t){this.#u=t}setQueryDefaults(t,e){this.#m.set((0,i.Ym)(t),{queryKey:t,defaultOptions:e})}getQueryDefaults(t){let e=[...this.#m.values()],s={};return e.forEach(e=>{(0,i.to)(t,e.queryKey)&&Object.assign(s,e.defaultOptions)}),s}setMutationDefaults(t,e){this.#y.set((0,i.Ym)(t),{mutationKey:t,defaultOptions:e})}getMutationDefaults(t){let e=[...this.#y.values()],s={};return e.forEach(e=>{(0,i.to)(t,e.mutationKey)&&Object.assign(s,e.defaultOptions)}),s}defaultQueryOptions(t){if(t._defaulted)return t;let e={...this.#u.queries,...this.getQueryDefaults(t.queryKey),...t,_defaulted:!0};return e.queryHash||(e.queryHash=(0,i.Rm)(e.queryKey,e)),void 0===e.refetchOnReconnect&&(e.refetchOnReconnect="always"!==e.networkMode),void 0===e.throwOnError&&(e.throwOnError=!!e.suspense),!e.networkMode&&e.persister&&(e.networkMode="offlineFirst"),e.queryFn===i.CN&&(e.enabled=!1),e}defaultMutationOptions(t){return t?._defaulted?t:{...this.#u.mutations,...t?.mutationKey&&this.getMutationDefaults(t.mutationKey),...t,_defaulted:!0}}clear(){this.#p.clear(),this.#s.clear()}}},521:function(t,e,s){"use strict";s.d(e,{t:function(){return i}});var i=function(){return null}},5925:function(t,e,s){"use strict";let i,a;s.d(e,{x7:function(){return td},ZP:function(){return tf}});var r,n=s(2265);let o={data:""},u=t=>"object"==typeof window?((t?t.querySelector("#_goober"):window._goober)||Object.assign((t||document.head).appendChild(document.createElement("style")),{innerHTML:" ",id:"_goober"})).firstChild:t||o,l=/(?:([\u0080-\uFFFF\w-%@]+) *:? *([^{;]+?);|([^;}{]*?) *{)|(}\s*)/g,c=/\/\*[^]*?\*\/|  +/g,h=/\n+/g,d=(t,e)=>{let s="",i="",a="";for(let r in t){let n=t[r];"@"==r[0]?"i"==r[1]?s=r+" "+n+";":i+="f"==r[1]?d(n,r):r+"{"+d(n,"k"==r[1]?"":e)+"}":"object"==typeof n?i+=d(n,e?e.replace(/([^,])+/g,t=>r.replace(/([^,]*:\S+\([^)]*\))|([^,])+/g,e=>/&/.test(e)?e.replace(/&/g,t):t?t+" "+e:e)):r):null!=n&&(r=/^--/.test(r)?r:r.replace(/[A-Z]/g,"-$&").toLowerCase(),a+=d.p?d.p(r,n):r+":"+n+";")}return s+(e&&a?e+"{"+a+"}":a)+i},f={},p=t=>{if("object"==typeof t){let e="";for(let s in t)e+=s+p(t[s]);return e}return t},m=(t,e,s,i,a)=>{var r;let n=p(t),o=f[n]||(f[n]=(t=>{let e=0,s=11;for(;e<t.length;)s=101*s+t.charCodeAt(e++)>>>0;return"go"+s})(n));if(!f[o]){let e=n!==t?t:(t=>{let e,s,i=[{}];for(;e=l.exec(t.replace(c,""));)e[4]?i.shift():e[3]?(s=e[3].replace(h," ").trim(),i.unshift(i[0][s]=i[0][s]||{})):i[0][e[1]]=e[2].replace(h," ").trim();return i[0]})(t);f[o]=d(a?{["@keyframes "+o]:e}:e,s?"":"."+o)}let u=s&&f.g?f.g:null;return s&&(f.g=f[o]),r=f[o],u?e.data=e.data.replace(u,r):-1===e.data.indexOf(r)&&(e.data=i?r+e.data:e.data+r),o},y=(t,e,s)=>t.reduce((t,i,a)=>{let r=e[a];if(r&&r.call){let t=r(s),e=t&&t.props&&t.props.className||/^go/.test(t)&&t;r=e?"."+e:t&&"object"==typeof t?t.props?"":d(t,""):!1===t?"":t}return t+i+(null==r?"":r)},"");function g(t){let e=this||{},s=t.call?t(e.p):t;return m(s.unshift?s.raw?y(s,[].slice.call(arguments,1),e.p):s.reduce((t,s)=>Object.assign(t,s&&s.call?s(e.p):s),{}):s,u(e.target),e.g,e.o,e.k)}g.bind({g:1});let v,b,C,w=g.bind({k:1});function x(t,e){let s=this||{};return function(){let i=arguments;function a(r,n){let o=Object.assign({},r),u=o.className||a.className;s.p=Object.assign({theme:b&&b()},o),s.o=/ *go\d+/.test(u),o.className=g.apply(s,i)+(u?" "+u:""),e&&(o.ref=n);let l=t;return t[0]&&(l=o.as||t,delete o.as),C&&l[0]&&C(o),v(l,o)}return e?e(a):a}}var O=t=>"function"==typeof t,S=(t,e)=>O(t)?t(e):t,q=(i=0,()=>(++i).toString()),E=()=>{if(void 0===a&&"u">typeof window){let t=matchMedia("(prefers-reduced-motion: reduce)");a=!t||t.matches}return a},A="default",D=(t,e)=>{let{toastLimit:s}=t.settings;switch(e.type){case 0:return{...t,toasts:[e.toast,...t.toasts].slice(0,s)};case 1:return{...t,toasts:t.toasts.map(t=>t.id===e.toast.id?{...t,...e.toast}:t)};case 2:let{toast:i}=e;return D(t,{type:t.toasts.find(t=>t.id===i.id)?1:0,toast:i});case 3:let{toastId:a}=e;return{...t,toasts:t.toasts.map(t=>t.id===a||void 0===a?{...t,dismissed:!0,visible:!1}:t)};case 4:return void 0===e.toastId?{...t,toasts:[]}:{...t,toasts:t.toasts.filter(t=>t.id!==e.toastId)};case 5:return{...t,pausedAt:e.time};case 6:let r=e.time-(t.pausedAt||0);return{...t,pausedAt:void 0,toasts:t.toasts.map(t=>({...t,pauseDuration:t.pauseDuration+r}))}}},P=[],k={toasts:[],pausedAt:void 0,settings:{toastLimit:20}},F={},$=(t,e=A)=>{F[e]=D(F[e]||k,t),P.forEach(([t,s])=>{t===e&&s(F[e])})},T=t=>Object.keys(F).forEach(e=>$(t,e)),M=t=>Object.keys(F).find(e=>F[e].toasts.some(e=>e.id===t)),Q=(t=A)=>e=>{$(e,t)},R={blank:4e3,error:4e3,success:2e3,loading:1/0,custom:4e3},I=(t={},e=A)=>{let[s,i]=(0,n.useState)(F[e]||k),a=(0,n.useRef)(F[e]);(0,n.useEffect)(()=>(a.current!==F[e]&&i(F[e]),P.push([e,i]),()=>{let t=P.findIndex(([t])=>t===e);t>-1&&P.splice(t,1)}),[e]);let r=s.toasts.map(e=>{var s,i,a;return{...t,...t[e.type],...e,removeDelay:e.removeDelay||(null==(s=t[e.type])?void 0:s.removeDelay)||(null==t?void 0:t.removeDelay),duration:e.duration||(null==(i=t[e.type])?void 0:i.duration)||(null==t?void 0:t.duration)||R[e.type],style:{...t.style,...null==(a=t[e.type])?void 0:a.style,...e.style}}});return{...s,toasts:r}},K=(t,e="blank",s)=>({createdAt:Date.now(),visible:!0,dismissed:!1,type:e,ariaProps:{role:"status","aria-live":"polite"},message:t,pauseDuration:0,...s,id:(null==s?void 0:s.id)||q()}),N=t=>(e,s)=>{let i=K(e,t,s);return Q(i.toasterId||M(i.id))({type:2,toast:i}),i.id},j=(t,e)=>N("blank")(t,e);j.error=N("error"),j.success=N("success"),j.loading=N("loading"),j.custom=N("custom"),j.dismiss=(t,e)=>{let s={type:3,toastId:t};e?Q(e)(s):T(s)},j.dismissAll=t=>j.dismiss(void 0,t),j.remove=(t,e)=>{let s={type:4,toastId:t};e?Q(e)(s):T(s)},j.removeAll=t=>j.remove(void 0,t),j.promise=(t,e,s)=>{let i=j.loading(e.loading,{...s,...null==s?void 0:s.loading});return"function"==typeof t&&(t=t()),t.then(t=>{let a=e.success?S(e.success,t):void 0;return a?j.success(a,{id:i,...s,...null==s?void 0:s.success}):j.dismiss(i),t}).catch(t=>{let a=e.error?S(e.error,t):void 0;a?j.error(a,{id:i,...s,...null==s?void 0:s.error}):j.dismiss(i)}),t};var _=1e3,U=(t,e="default")=>{let{toasts:s,pausedAt:i}=I(t,e),a=(0,n.useRef)(new Map).current,r=(0,n.useCallback)((t,e=_)=>{if(a.has(t))return;let s=setTimeout(()=>{a.delete(t),o({type:4,toastId:t})},e);a.set(t,s)},[]);(0,n.useEffect)(()=>{if(i)return;let t=Date.now(),a=s.map(s=>{if(s.duration===1/0)return;let i=(s.duration||0)+s.pauseDuration-(t-s.createdAt);if(i<0){s.visible&&j.dismiss(s.id);return}return setTimeout(()=>j.dismiss(s.id,e),i)});return()=>{a.forEach(t=>t&&clearTimeout(t))}},[s,i,e]);let o=(0,n.useCallback)(Q(e),[e]),u=(0,n.useCallback)(()=>{o({type:5,time:Date.now()})},[o]),l=(0,n.useCallback)((t,e)=>{o({type:1,toast:{id:t,height:e}})},[o]),c=(0,n.useCallback)(()=>{i&&o({type:6,time:Date.now()})},[i,o]),h=(0,n.useCallback)((t,e)=>{let{reverseOrder:i=!1,gutter:a=8,defaultPosition:r}=e||{},n=s.filter(e=>(e.position||r)===(t.position||r)&&e.height),o=n.findIndex(e=>e.id===t.id),u=n.filter((t,e)=>e<o&&t.visible).length;return n.filter(t=>t.visible).slice(...i?[u+1]:[0,u]).reduce((t,e)=>t+(e.height||0)+a,0)},[s]);return(0,n.useEffect)(()=>{s.forEach(t=>{if(t.dismissed)r(t.id,t.removeDelay);else{let e=a.get(t.id);e&&(clearTimeout(e),a.delete(t.id))}})},[s,r]),{toasts:s,handlers:{updateHeight:l,startPause:u,endPause:c,calculateOffset:h}}},H=w`
from {
  transform: scale(0) rotate(45deg);
	opacity: 0;
}
to {
 transform: scale(1) rotate(45deg);
  opacity: 1;
}`,V=w`
from {
  transform: scale(0);
  opacity: 0;
}
to {
  transform: scale(1);
  opacity: 1;
}`,L=w`
from {
  transform: scale(0) rotate(90deg);
	opacity: 0;
}
to {
  transform: scale(1) rotate(90deg);
	opacity: 1;
}`,z=x("div")`
  width: 20px;
  opacity: 0;
  height: 20px;
  border-radius: 10px;
  background: ${t=>t.primary||"#ff4b4b"};
  position: relative;
  transform: rotate(45deg);

  animation: ${H} 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)
    forwards;
  animation-delay: 100ms;

  &:after,
  &:before {
    content: '';
    animation: ${V} 0.15s ease-out forwards;
    animation-delay: 150ms;
    position: absolute;
    border-radius: 3px;
    opacity: 0;
    background: ${t=>t.secondary||"#fff"};
    bottom: 9px;
    left: 4px;
    height: 2px;
    width: 12px;
  }

  &:before {
    animation: ${L} 0.15s ease-out forwards;
    animation-delay: 180ms;
    transform: rotate(90deg);
  }
`,Z=w`
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
`,G=x("div")`
  width: 12px;
  height: 12px;
  box-sizing: border-box;
  border: 2px solid;
  border-radius: 100%;
  border-color: ${t=>t.secondary||"#e0e0e0"};
  border-right-color: ${t=>t.primary||"#616161"};
  animation: ${Z} 1s linear infinite;
`,B=w`
from {
  transform: scale(0) rotate(45deg);
	opacity: 0;
}
to {
  transform: scale(1) rotate(45deg);
	opacity: 1;
}`,X=w`
0% {
	height: 0;
	width: 0;
	opacity: 0;
}
40% {
  height: 0;
	width: 6px;
	opacity: 1;
}
100% {
  opacity: 1;
  height: 10px;
}`,Y=x("div")`
  width: 20px;
  opacity: 0;
  height: 20px;
  border-radius: 10px;
  background: ${t=>t.primary||"#61d345"};
  position: relative;
  transform: rotate(45deg);

  animation: ${B} 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)
    forwards;
  animation-delay: 100ms;
  &:after {
    content: '';
    box-sizing: border-box;
    animation: ${X} 0.2s ease-out forwards;
    opacity: 0;
    animation-delay: 200ms;
    position: absolute;
    border-right: 2px solid;
    border-bottom: 2px solid;
    border-color: ${t=>t.secondary||"#fff"};
    bottom: 6px;
    left: 6px;
    height: 10px;
    width: 6px;
  }
`,J=x("div")`
  position: absolute;
`,W=x("div")`
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  min-width: 20px;
  min-height: 20px;
`,tt=w`
from {
  transform: scale(0.6);
  opacity: 0.4;
}
to {
  transform: scale(1);
  opacity: 1;
}`,te=x("div")`
  position: relative;
  transform: scale(0.6);
  opacity: 0.4;
  min-width: 20px;
  animation: ${tt} 0.3s 0.12s cubic-bezier(0.175, 0.885, 0.32, 1.275)
    forwards;
`,ts=({toast:t})=>{let{icon:e,type:s,iconTheme:i}=t;return void 0!==e?"string"==typeof e?n.createElement(te,null,e):e:"blank"===s?null:n.createElement(W,null,n.createElement(G,{...i}),"loading"!==s&&n.createElement(J,null,"error"===s?n.createElement(z,{...i}):n.createElement(Y,{...i})))},ti=t=>`
0% {transform: translate3d(0,${-200*t}%,0) scale(.6); opacity:.5;}
100% {transform: translate3d(0,0,0) scale(1); opacity:1;}
`,ta=t=>`
0% {transform: translate3d(0,0,-1px) scale(1); opacity:1;}
100% {transform: translate3d(0,${-150*t}%,-1px) scale(.6); opacity:0;}
`,tr=x("div")`
  display: flex;
  align-items: center;
  background: #fff;
  color: #363636;
  line-height: 1.3;
  will-change: transform;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1), 0 3px 3px rgba(0, 0, 0, 0.05);
  max-width: 350px;
  pointer-events: auto;
  padding: 8px 10px;
  border-radius: 8px;
`,tn=x("div")`
  display: flex;
  justify-content: center;
  margin: 4px 10px;
  color: inherit;
  flex: 1 1 auto;
  white-space: pre-line;
`,to=(t,e)=>{let s=t.includes("top")?1:-1,[i,a]=E()?["0%{opacity:0;} 100%{opacity:1;}","0%{opacity:1;} 100%{opacity:0;}"]:[ti(s),ta(s)];return{animation:e?`${w(i)} 0.35s cubic-bezier(.21,1.02,.73,1) forwards`:`${w(a)} 0.4s forwards cubic-bezier(.06,.71,.55,1)`}},tu=n.memo(({toast:t,position:e,style:s,children:i})=>{let a=t.height?to(t.position||e||"top-center",t.visible):{opacity:0},r=n.createElement(ts,{toast:t}),o=n.createElement(tn,{...t.ariaProps},S(t.message,t));return n.createElement(tr,{className:t.className,style:{...a,...s,...t.style}},"function"==typeof i?i({icon:r,message:o}):n.createElement(n.Fragment,null,r,o))});r=n.createElement,d.p=void 0,v=r,b=void 0,C=void 0;var tl=({id:t,className:e,style:s,onHeightUpdate:i,children:a})=>{let r=n.useCallback(e=>{if(e){let s=()=>{i(t,e.getBoundingClientRect().height)};s(),new MutationObserver(s).observe(e,{subtree:!0,childList:!0,characterData:!0})}},[t,i]);return n.createElement("div",{ref:r,className:e,style:s},a)},tc=(t,e)=>{let s=t.includes("top"),i=t.includes("center")?{justifyContent:"center"}:t.includes("right")?{justifyContent:"flex-end"}:{};return{left:0,right:0,display:"flex",position:"absolute",transition:E()?void 0:"all 230ms cubic-bezier(.21,1.02,.73,1)",transform:`translateY(${e*(s?1:-1)}px)`,...s?{top:0}:{bottom:0},...i}},th=g`
  z-index: 9999;
  > * {
    pointer-events: auto;
  }
`,td=({reverseOrder:t,position:e="top-center",toastOptions:s,gutter:i,children:a,toasterId:r,containerStyle:o,containerClassName:u})=>{let{toasts:l,handlers:c}=U(s,r);return n.createElement("div",{"data-rht-toaster":r||"",style:{position:"fixed",zIndex:9999,top:16,left:16,right:16,bottom:16,pointerEvents:"none",...o},className:u,onMouseEnter:c.startPause,onMouseLeave:c.endPause},l.map(s=>{let r=s.position||e,o=tc(r,c.calculateOffset(s,{reverseOrder:t,gutter:i,defaultPosition:e}));return n.createElement(tl,{id:s.id,key:s.id,onHeightUpdate:c.updateHeight,className:s.visible?th:"",style:o},"custom"===s.type?S(s.message,s):a?a(s):n.createElement(tu,{toast:s,position:r}))}))},tf=j}}]);