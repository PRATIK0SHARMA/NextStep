import {request} from './api.js';

const $=s=>document.querySelector(s);

const escape=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

const names={fan:'Fan',refrigerator:'Refrigerator',washing_machine:'Washing machine',unknown:'Appliance'};

const symbols={fan:'✣',refrigerator:'▥',washing_machine:'◎',unknown:'⌂'};

const dateLabel=s=>s?new Date(`${s}T12:00:00`).toLocaleDateString('en-IN',{day:'numeric',month:'short'}):'Not set';

const money=n=>`₹${Number(n).toLocaleString('en-IN')}`;

let state={tasks:[],bookings:[],active:null},view='workspace',busy=false,timer,config={mode:'demo'},recognition;

const task=()=>state.tasks.find(t=>t.id===state.active);

const findOptions=t=>t.options;

function modeLabel(){return config.mode==='demo'?'Rule-based demo':config.mode==='ollama'?'Local AI':'Cloud AI';}

function localDate(offset=0){const d=new Date(config.today+'T12:00:00Z');d.setUTCDate(d.getUTCDate()+offset);return d.toISOString().slice(0,10);}

function mapOption(o){return o?{...o,date:o.service_date}:null;}

function mapTask(t){return {...t,appliance:t.appliance||'unknown',zone:t.zone||'not set',date:t.preferred_date,time:t.time_preference,budget:t.max_visit_fee,issue:t.issue_description,options:t.options.map(mapOption),selected:mapOption(t.selected),booking:mapOption(t.booking)};}

function rebuild(){state.bookings=state.tasks.filter(t=>t.booking).map(t=>t.booking);}

function upsert(raw){const t=mapTask(raw);const i=state.tasks.findIndex(x=>x.id===t.id);const previous=i<0?0:state.tasks[i].messages.length;if(i<0)state.tasks.unshift(t);else state.tasks[i]=t;state.active=t.id;rebuild();const reply=t.messages.slice(previous).filter(m=>m.role==='assistant').at(-1);if(reply)queueMicrotask(()=>{if(state.active===t.id&&view==='workspace'&&autoSpeak)speakReply(reply.text);});return t;}

function toast(text){$('#toast').textContent=text;$('#toast').classList.add('show');clearTimeout(timer);timer=setTimeout(()=>$('#toast').classList.remove('show'),5500);}

async function refresh(){const rows=await request('/tasks',undefined,'GET');state.tasks=rows.map(mapTask);rebuild();}

function newTask(){state.active=null;view='workspace';history.replaceState(null,'','/');render();}

function sidebar(){

  const saved=state.tasks.filter(t=>t.status!=='completed');

  $('#saved-count').textContent=saved.length;$('#booking-count').textContent=state.bookings.length;

  $('#recent-list').innerHTML=state.tasks.slice(0,4).map(t=>`<button class="recent" data-resume="${escape(t.id)}">${escape(names[t.appliance])} repair<small>${escape(t.zone)} · ${t.status==='completed'?'Booked':'Ready to resume'}</small></button>`).join('')||'<p class="muted" style="padding:0 10px;color:#98b7b4">Your requests will appear here.</p>';

  document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===view));

  $('#save-exit').hidden=view!=='workspace'||!task()||task().status==='completed';

  $('#mode-badge').textContent=modeLabel();

}

function summary(t){return `<section class="panel summary"><div class="summary-head"><strong>Request details</strong>${t&&t.status!=='completed'?'<button class="text-button" data-edit>Edit</button>':''}</div><div class="appliance-tile"><span class="appliance-symbol">${t?symbols[t.appliance]:'⌂'}</span><div><strong>${t?escape(names[t.appliance])+' repair':'Your next repair'}</strong><small>${t?'Home appliance service':'Start with a few details'}</small></div></div><dl><div><dt>Service zone</dt><dd>${t?escape(t.zone[0].toUpperCase()+t.zone.slice(1)):'—'}</dd></div><div><dt>Preferred date</dt><dd>${t?dateLabel(t.date):'—'}</dd></div><div><dt>Time</dt><dd>${t?escape(t.time==='any'?'Any time':t.time):'—'}</dd></div><div><dt>Visit fee limit</dt><dd>${t?(t.budget===null?'No limit':money(t.budget)):'—'}</dd></div></dl><p class="summary-note">Inspection fee only. Parts and repair charges are not included.</p></section>`;}

function steps(t){const s=!t?0:t.status==='completed'?3:t.selected?2:1;return `<section class="panel steps"><strong>A little closer to done</strong>${['Tell us what you need','Choose your appointment','Review & confirm'].map((text,i)=>`<div class="step ${i<s?'done':i===s?'current':''}"><span>${i<s?'✓':i+1}</span>${text}</div>`).join('')}</section><p class="rail-note">↺ &nbsp; You can leave at any time.<br>Your progress is saved securely in this workspace.</p>`;}

function providerCards(t){const options=findOptions(t,state.bookings);if(!options.length)return `<div class="empty"><h2>No matching appointments</h2><p>Try another date, time, or visit fee limit. Available slots cover the next 14 days.</p><button class="secondary" data-edit>Change preferences</button></div>`;

return `<div class="options-heading"><strong>${options.length} options for your repair</strong><small>Sorted by lowest visit fee</small></div>${options.map((p,i)=>`<article class="provider ${i===0?'best':''}"><div class="provider-icon">${p.name.slice(0,2)}</div><div>${i===0?'<span class="recommend">LOWEST VISIT FEE</span>':''}<strong>${p.name}</strong><p>${dateLabel(p.date)} · ${p.start_hour}:00–${p.end_hour}:00 IST</p><p>${escape(t.zone)} zone · ${escape(names[t.appliance])} repair</p></div><div class="price">${money(p.visit_fee)}<small>visit fee</small><button class="select-slot" data-select="${p.slot_id}">Choose slot</button></div></article>`).join('')}`;}

function result(t){if(t.status==='completed'){const b=state.bookings.find(b=>b.task_id===t.id);return `<div class="success"><div class="tick">✓</div><h2>One less thing on your mind.</h2><p>Your demo appointment with <strong>${escape(b.name)}</strong> is confirmed.</p><p>${dateLabel(b.date)} · ${b.start_hour}:00–${b.end_hour}:00 IST<br>Visit fee: <strong>${money(b.visit_fee)}</strong></p><p>Reference: <strong>${b.id}</strong></p><button class="secondary" data-view="bookings">View appointments</button></div>`;}

if(t.selected){const p=t.selected;return `<div class="confirmation"><span class="eyebrow">ONE LAST CHECK</span><h2>Ready to book?</h2><p><strong>${p.name}</strong><br>${dateLabel(p.date)} · ${p.start_hour}:00–${p.end_hour}:00 IST<br>${escape(names[t.appliance])} repair · ${escape(t.zone)} zone</p><p>Visit fee: <strong>${money(p.visit_fee)}</strong></p><p class="muted">This creates a demo appointment only. No payment will be taken.</p><div class="buttons"><button class="primary" id="confirm">Confirm demo booking</button><button class="secondary" id="back-options">Other options</button></div></div>`;}return providerCards(t);}

function workspace(){const t=task();return `<div class="intro"><div><span class="eyebrow">A LITTLE HELP. A LOT LESS HASSLE.</span><h1>${t?'Let’s take the next step.':'What can we take care of?'}</h1><p>${t?'Your repair request, all in one place.':'Find a repair appointment that fits your day.'}</p></div><span class="autosave">↺ &nbsp; Progress saved to your workspace</span></div><div class="workspace-grid"><section class="panel"><div class="panel-head"><span class="assistant-logo">✳</span><div><strong>NextStep assistant</strong><small>Here to help you get it done</small></div><span class="live-pill">${escape(modeLabel())}</span></div>${t?`<div class="conversation" aria-live="polite">${t.messages.map(m=>`<div class="message ${m.role}"><span class="who">${m.role==='user'?'YOU':'NEXTSTEP'}</span>${escape(m.text)}</div>`).join('')}</div><div class="options">${result(t)}</div>`:`<div class="start-content"><div class="initial-art">✳</div><h2>A small fix starts here.</h2><p>Tell me which appliance needs attention. We’ll find a suitable appointment, and you can finish whenever you’re ready.</p><div class="start-services">${Object.keys(names).map(a=>`<button class="service-button" data-start="${a}"><span>${symbols[a]}</span>${names[a]}</button>`).join('')}</div><button class="chip" id="sample">Try: fan repair tomorrow under ₹500</button></div>`}<div class="composer-wrap"><form id="chat-form" class="composer"><textarea id="chat-input" rows="1" aria-label="Message NextStep" maxlength="1000" placeholder="${t?'Change the budget, date, or time…':'Tell me what needs fixing…'}" ${t?.status==='completed'?'disabled':''}></textarea><button type="button" class="voice-button" id="voice" aria-label="Dictate message">◉</button><button class="send" aria-label="Send message" ${t?.status==='completed'?'disabled':''}>↑</button></form><div class="composer-foot"><span>${config.mode==='demo'?'Rule-based demo · Edit for exact preferences':'AI assisted · review before confirming'}</span><span style="display:flex;gap:8px;flex-wrap:wrap"><button type="button" id="speech-toggle" class="text-button" aria-pressed="false">Speaker: off</button><button type="button" id="stop-speaking" class="text-button" disabled>Stop speaking</button><button type="button" id="read-reply" class="text-button" aria-label="Read latest assistant reply aloud">Read reply</button></span></div></div></section><aside class="right-rail">${summary(t)}${steps(t)}</aside></div>`;}

function listings(){const isBooking=view==='bookings';const rows=isBooking?state.bookings:state.tasks.filter(t=>t.status!=='completed');return `<span class="eyebrow">${isBooking?'ALL TAKEN CARE OF':'RIGHT WHERE YOU LEFT OFF'}</span><h1>${isBooking?'Your appointments':'Saved requests'}</h1><p class="page-description">${isBooking?'Your confirmed demo appointments, in one place.':'Come back when it works for you. We’ll check availability again.'}</p>${rows.length?rows.slice().reverse().map(r=>{const t=isBooking?state.tasks.find(t=>t.id===r.task_id):r;return `<article class="panel list-card"><div><span class="status-label">${isBooking?'Confirmed · demo':'Saved for later'}</span><h2>${escape(names[t.appliance])} repair${isBooking?' · '+escape(r.name):''}</h2><p>${dateLabel(t.date)} · ${escape(t.zone)}${isBooking?' · '+money(r.visit_fee):''}</p>${isBooking?`<small class="muted">${r.id} · ${r.start_hour}:00–${r.end_hour}:00 IST</small>`:''}</div><button class="secondary" data-resume="${t.id}">${isBooking?'View details':'Resume request'}</button></article>`;}).join(''):`<section class="panel empty"><h2>${isBooking?'No appointments yet':'Nothing left unfinished'}</h2><p>${isBooking?'Your confirmed appointments will appear here.':'Start a repair request and we’ll keep your progress.'}</p><button class="primary" data-new>Start a repair request</button></section>`}`;}

function render(){sidebar();$('#page-title').textContent=view==='workspace'?'Repair assistant':view==='saved'?'Saved requests':'Appointments';$('#main').innerHTML=view==='workspace'?workspace():listings();const c=$('.conversation');if(c)c.scrollTop=c.scrollHeight;const voice=$('#voice');if(voice&&!('SpeechRecognition' in window||'webkitSpeechRecognition' in window))voice.hidden=true;speechControls();}

function openDetails(appliance='fan',prefill={}){const t=task();const values={appliance,zone:'central',date:localDate(1),time:'any',budget:'',issue:'',...(t||{}),...prefill};if(values.appliance==='unknown')values.appliance='fan';if(values.zone==='not set')values.zone='central';if(!values.date)values.date=localDate(1);const form=$('#details-form');for(const key of ['appliance','zone','date','time','budget','issue'])form.elements[key].value=values[key]??'';form.elements.date.min=localDate(1);form.elements.date.max=localDate(14);$('#edit-dialog').showModal();}

async function action(fn){if(busy)return;busy=true;document.body.classList.add('working');try{await fn();}catch(e){toast(e.name==='TimeoutError'?'The request timed out. Refresh before retrying confirmation.':e.message);if(e.status===409){await refresh().catch(()=>{});render();}if(e.status===401)$('#access-dialog').showModal();}finally{busy=false;document.body.classList.remove('working');}}

async function resume(id){upsert(await request(`/tasks/${id}/resume`,{}));view='workspace';history.replaceState(null,'',`/?task=${id}`);render();}

async function selectSlot(id){const t=task();upsert(await request(`/tasks/${t.id}/select`,{slot_id:Number(id),revision:t.revision}));render();}

async function confirmBooking(){const t=task();if(!t?.selected||t.status==='completed')return;const key=`nextstep-confirm-${t.id}-${t.revision}-${t.selected.slot_id}`;let id=sessionStorage.getItem(key);if(!id){id=crypto.randomUUID();sessionStorage.setItem(key,id);}upsert(await request(`/tasks/${t.id}/confirm`,{slot_id:t.selected.slot_id,revision:t.revision,request_id:id,confirmed:true}));sessionStorage.removeItem(key);render();}

async function chat(text){stopSpeaking();let t=task();if(!t)t=upsert(await request('/tasks',{}));const result=await request(`/tasks/${t.id}/messages`,{text,revision:t.revision});upsert(result);history.replaceState(null,'',`/?task=${t.id}`);render();if(result.agent_status==='unavailable')toast('AI unavailable. Use Edit details to continue; no automatic fallback was used.');}

// Speech output is opt-in for this page session; no old history is read automatically.
const speechAvailable='speechSynthesis' in window && 'SpeechSynthesisUtterance' in window;
let autoSpeak=false, speechGeneration=0, currentUtterance=null;
function speechControls(){
 const toggle=$('#speech-toggle'),stop=$('#stop-speaking');
 if(toggle){toggle.disabled=!speechAvailable;toggle.textContent=speechAvailable?(autoSpeak?'Speaker: on':'Speaker: off'):'Speech unavailable';toggle.setAttribute('aria-pressed',String(autoSpeak));}
 if(stop)stop.disabled=!currentUtterance;
}
function stopSpeaking(){speechGeneration++;currentUtterance=null;if(speechAvailable)window.speechSynthesis.cancel();speechControls();}
function speakReply(text){
 if(!speechAvailable)return toast('Speech output is unavailable in this browser.');
 if(recognition)return;
 stopSpeaking();
 const generation=speechGeneration;
 const utterance=new SpeechSynthesisUtterance(String(text).replace(/₹/g,' rupees '));
 currentUtterance=utterance;utterance.lang='en-IN';utterance.rate=1;
 const voices=window.speechSynthesis.getVoices();
 const voice=voices.find(v=>v.lang.toLowerCase()==='en-in')||voices.find(v=>v.lang.toLowerCase().startsWith('en'));
 if(voice)utterance.voice=voice;
 utterance.onend=()=>{if(generation===speechGeneration){currentUtterance=null;speechControls();}};
 utterance.onerror=e=>{if(generation!==speechGeneration)return;currentUtterance=null;speechControls();if(!['canceled','interrupted'].includes(e.error))toast('Could not play speech. Try Read reply, or check your browser audio settings.');};
 try{window.speechSynthesis.speak(utterance);speechControls();}catch(e){currentUtterance=null;speechControls();toast('Speech could not start. Try Read reply.');}
}
window.addEventListener('pagehide',stopSpeaking);
document.addEventListener('visibilitychange',()=>{if(document.hidden)stopSpeaking();});

function dictate(){stopSpeaking();const SR=window.SpeechRecognition||window.webkitSpeechRecognition;if(!SR)return toast('Voice input is unavailable in this browser.');if(recognition){recognition.stop();return;}recognition=new SR();recognition.lang='en-IN';recognition.interimResults=false;recognition.onresult=e=>{const input=$('#chat-input');if(input){input.value=e.results[0][0].transcript;input.focus();}toast('Review the transcript, then press Send.');};recognition.onerror=()=>toast('Voice input unavailable. You can type instead.');recognition.onend=()=>{recognition=null;const b=$('#voice');if(b){b.classList.remove('listening');b.setAttribute('aria-label','Dictate message');}};recognition.start();$('#voice').classList.add('listening');$('#voice').setAttribute('aria-label','Stop listening');toast('Listening… your browser may use its speech service.');}

// Event delegation keeps dynamic screens simple and makes all actions share error handling.

document.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;

 if(b.id==='close-dialog')return $('#edit-dialog').close();

 if(b.id==='help')return $('#help-dialog').showModal();

 if(b.id==='close-help')return $('#help-dialog').close();

 if(b.id==='mcp-settings')return $('#mcp-dialog').showModal();

 if(b.id==='close-mcp')return $('#mcp-dialog').close();

 if(b.id==='voice')return dictate();

 if(b.id==='speech-toggle'){autoSpeak=!autoSpeak;if(!autoSpeak)stopSpeaking();speechControls();if(autoSpeak)speakReply('Spoken replies are now on.');return;}
 if(b.id==='stop-speaking')return stopSpeaking();
 if(b.id==='read-reply'){const reply=task()?.messages.filter(m=>m.role==='assistant').at(-1)?.text;if(reply)speakReply(reply);else toast('Start a request to hear a reply.');return;}
 if(b.dataset.view||b.dataset.resume||b.hasAttribute('data-new')||b.id==='new-task'||b.id==='save-exit')stopSpeaking();

 if(b.hasAttribute('data-edit'))return openDetails();

 if(b.dataset.start)return openDetails(b.dataset.start);

 if(b.id==='sample')return openDetails('fan',{budget:500,time:'afternoon',issue:'My fan is making a rattling sound.'});

 action(async()=>{

  if(b.dataset.view){view=b.dataset.view;await refresh();render();}

  else if(b.hasAttribute('data-new')||b.id==='new-task')newTask();

  else if(b.dataset.resume)await resume(b.dataset.resume);

  else if(b.id==='save-exit'){view='saved';await refresh();render();toast('Saved to your workspace. Resume whenever you’re ready.');}

  else if(b.dataset.select)await selectSlot(b.dataset.select);

  else if(b.id==='back-options'){const t=task();upsert(await request(`/tasks/${t.id}`,{revision:t.revision},'PATCH'));render();}

  else if(b.id==='confirm')await confirmBooking();

  else if(b.id==='mint-token'){const data=await request('/mcp-token',{});$('#token-result').innerHTML=`<label>MCP endpoint<input readonly value="${escape(data.url)}"></label><label>Bearer token<textarea readonly rows="3">${escape(data.token)}</textarea></label><p class="muted">Expires ${escape(data.expires_at)}</p>`;}

  else if(b.id==='revoke-token'){await request('/mcp-token',undefined,'DELETE');$('#token-result').textContent='Token revoked.';}

 });

});

$('#details-form').addEventListener('submit',e=>{e.preventDefault();const form=new FormData(e.target);const details={appliance:form.get('appliance'),zone:form.get('zone'),preferred_date:form.get('date'),time_preference:form.get('time'),max_visit_fee:form.get('budget')===''?null:Number(form.get('budget')),issue_description:form.get('issue').trim()};if(!details.issue_description)return;action(async()=>{const t=task();upsert(t?await request(`/tasks/${t.id}`,{...details,revision:t.revision},'PATCH'):await request('/tasks',details));$('#edit-dialog').close();view='workspace';history.replaceState(null,'',`/?task=${state.active}`);render();});});

$('#access-form').addEventListener('submit',e=>{e.preventDefault();action(async()=>{try{await request('/session',{access_code:new FormData(e.target).get('access_code')});$('#access-dialog').close();await refresh();render();}catch(err){$('#access-error').textContent=err.message;}});});

$('#access-dialog').addEventListener('cancel',e=>e.preventDefault());

document.addEventListener('submit',e=>{if(e.target.id!=='chat-form')return;e.preventDefault();const text=$('#chat-input').value.trim();if(text)action(()=>chat(text));});

document.addEventListener('keydown',e=>{if(e.target.id==='chat-input'&&e.key==='Enter'&&!e.shiftKey){e.preventDefault();$('#chat-form').requestSubmit();}});

async function init(){try{config=await request('/config',undefined,'GET');try{await request('/session',{});}catch(e){if(e.status===401){render();$('#access-dialog').showModal();return;}throw e;}await refresh();const id=new URLSearchParams(location.search).get('task');if(id&&state.tasks.some(t=>t.id===id))await resume(id);else render();}catch(e){$('#main').innerHTML='<section class="panel empty"><h2>Could not open the workspace</h2><p>Check that the Python server is running, then refresh this page.</p></section>';toast(e.message);}}

init();
