import json
import uuid
from datetime import timedelta
from .db import transaction, today, now
from .schemas import Details

class DomainError(Exception):
    def __init__(self, status, message):
        self.status, self.message = status, message
        super().__init__(message)

def audit(db, owner, tid, event, details=None):
    db.execute('INSERT INTO audit(session_id,task_id,event,details,created_at) VALUES(?,?,?,?,?)',
               (owner,tid,event,json.dumps(details or {}),now()))

def say(db, tid, text, role='assistant'):
    db.execute('INSERT INTO messages(task_id,role,text,created_at) VALUES(?,?,?,?)',(tid,role,text,now()))

def owned(db, owner, tid):
    row=db.execute('SELECT * FROM tasks WHERE id=? AND session_id=?',(tid,owner)).fetchone()
    if row is None: raise DomainError(404,'Request not found')
    return dict(row)

def require_revision(t, revision):
    if t['revision'] != revision:
        raise DomainError(409,'This request changed. Refresh it before continuing.')
    if t['status']=='completed':
        raise DomainError(409,'This appointment is already confirmed. Start a new request for another repair.')

def missing(t):
    return [label for key,label in [('appliance','appliance'),('zone','service zone'),('preferred_date','preferred date'),('issue_description','a short issue description')] if not t.get(key)]

def options(db,t):
    if missing(t): return []
    if not today().isoformat() < t['preferred_date'] <= (today()+timedelta(days=14)).isoformat(): return []
    rows=db.execute('''SELECT s.id AS slot_id,s.provider_id,s.service_date,s.start_hour,s.end_hour,
        p.name,p.visit_fee,p.appliances,p.zones FROM slots s JOIN providers p ON p.id=s.provider_id
        LEFT JOIN bookings b ON b.slot_id=s.id WHERE s.service_date=? AND b.id IS NULL
        ORDER BY p.visit_fee,p.id,s.start_hour''',(t['preferred_date'],)).fetchall()
    result=[]
    for r in rows:
        r=dict(r)
        if t['appliance'] not in json.loads(r.pop('appliances')) or t['zone'] not in json.loads(r.pop('zones')): continue
        if t['max_visit_fee'] is not None and r['visit_fee']>t['max_visit_fee']: continue
        if t['time_preference']=='morning' and r['start_hour']>=12: continue
        if t['time_preference']=='afternoon' and r['start_hour']<12: continue
        result.append(r)
    return result

def displayed_options(db,t):
    seen=set(); result=[]
    for o in options(db,t):
        if o['provider_id'] not in seen:
            result.append(o);seen.add(o['provider_id'])
        if len(result)==3: break
    return result

def booking_row(db,tid):
    row=db.execute('''SELECT b.*,s.service_date,s.start_hour,s.end_hour,p.name FROM bookings b
        JOIN slots s ON s.id=b.slot_id JOIN providers p ON p.id=s.provider_id WHERE b.task_id=?''',(tid,)).fetchone()
    if not row: return None
    data=dict(row);data.pop('session_id',None);return data

def snapshot(db,owner,tid):
    t=owned(db,owner,tid)
    t.pop('session_id',None)
    t['messages']=[dict(r) for r in db.execute('SELECT role,text,created_at FROM messages WHERE task_id=? ORDER BY id',(tid,))]
    t['options']=displayed_options(db,t) if t['status']!='completed' else []
    t['selected']=next((o for o in options(db,t) if o['slot_id']==t['selected_slot_id']),None) if t['status']!='completed' else None
    t['booking']=booking_row(db,tid)
    t['missing']=missing(t)
    t['audit']=[dict(r) for r in db.execute('SELECT event,details,created_at FROM audit WHERE task_id=? ORDER BY id DESC LIMIT 20',(tid,))]
    return t

def create(owner, details=None):
    data=Details.model_validate(details or {}).model_dump(mode='json')
    tid=str(uuid.uuid4())
    with transaction() as db:
        if db.execute('SELECT COUNT(*) FROM tasks WHERE session_id=?',(owner,)).fetchone()[0]>=100:
            raise DomainError(429,'This workspace has reached its 100-request limit.')
        db.execute('''INSERT INTO tasks(id,session_id,appliance,zone,preferred_date,time_preference,max_visit_fee,
          issue_description,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)''',
          (tid,owner,data['appliance'],data['zone'],data['preferred_date'],data['time_preference'],data['max_visit_fee'],data['issue_description'],now(),now()))
        t=owned(db,owner,tid)
        if not missing(t): db.execute("UPDATE tasks SET status='choosing_option' WHERE id=?",(tid,))
        if missing(t):
            say(db,tid,'To find the right visit, I still need: '+', '.join(missing(t))+'. Tell me here or use Edit details.')
        else:
            say(db,tid,f"{data['appliance'].replace('_',' ').title()} repair in {data['zone']}, {data['preferred_date']}, {data['time_preference']}. {data['issue_description']}",'user')
            say(db,tid,'Your preferences are saved. Here are matching appointments, sorted by visit fee. Select one to review before confirming.' if displayed_options(db,t) else 'No appointments match yet. Try changing the date, time, or visit-fee limit.')
        audit(db,owner,tid,'request_created')
        return snapshot(db,owner,tid)

def get(owner,tid,resume=False):
    with transaction() as db:
        t=owned(db,owner,tid)
        if resume and t['status']!='completed':
            current=options(db,t)
            if t['selected_slot_id'] is not None and not any(o['slot_id']==t['selected_slot_id'] for o in current):
                db.execute("UPDATE tasks SET selected_slot_id=NULL,status='choosing_option',revision=revision+1,updated_at=? WHERE id=?",(now(),tid))
                say(db,tid,'Welcome back. Your previous slot is no longer available. Your preferences are saved; please choose a fresh option.')
            else: say(db,tid,'Welcome back. Your request is saved, and I have checked availability again. Continue when you are ready.')
            audit(db,owner,tid,'request_resumed')
        return snapshot(db,owner,tid)

def list_tasks(owner):
    with transaction() as db:
        rows=db.execute('SELECT id FROM tasks WHERE session_id=? ORDER BY updated_at DESC',(owner,)).fetchall()
        return [snapshot(db,owner,r['id']) for r in rows]

def update(owner,tid,revision,changes):
    allowed=set(Details.model_fields)
    if not set(changes)<=allowed: raise DomainError(422,'Unknown request fields')
    with transaction() as db:
        t=owned(db,owner,tid);require_revision(t,revision)
        merged={k:t[k] for k in allowed};merged.update(changes)
        data=Details.model_validate(merged).model_dump(mode='json')
        state='collecting_details' if missing(data) else 'choosing_option'
        db.execute('''UPDATE tasks SET appliance=?,zone=?,preferred_date=?,time_preference=?,max_visit_fee=?,
            issue_description=?,status=?,selected_slot_id=NULL,revision=revision+1,updated_at=? WHERE id=?''',
            (data['appliance'],data['zone'],data['preferred_date'],data['time_preference'],data['max_visit_fee'],data['issue_description'],state,now(),tid))
        audit(db,owner,tid,'preferences_updated',{'fields':sorted(changes),'revision':revision+1})
        text='Preferences saved. '
        if missing(data): text+='I still need: '+', '.join(missing(data))+'.'
        elif not displayed_options(db,owned(db,owner,tid)): text+='No slots match. Try another date, time, zone, or visit-fee limit.'
        else: text+='I found matching appointments below. Choose one to review before booking.'
        say(db,tid,text)
        return snapshot(db,owner,tid)

def select(owner,tid,revision,slot_id):
    with transaction() as db:
        t=owned(db,owner,tid);require_revision(t,revision)
        option=next((o for o in options(db,t) if o['slot_id']==slot_id),None)
        if option is None: raise DomainError(409,'This slot is unavailable or does not match your latest preferences.')
        db.execute("UPDATE tasks SET selected_slot_id=?,status='awaiting_confirmation',revision=revision+1,updated_at=? WHERE id=?",(slot_id,now(),tid))
        audit(db,owner,tid,'option_selected',{'slot_id':slot_id,'revision':revision+1})
        say(db,tid,f"You selected {option['name']}. Review the date, time, and visit fee, then use Confirm booking. No appointment has been created yet.")
        return snapshot(db,owner,tid)

def confirm(owner,tid,revision,slot_id,request_id):
    with transaction() as db:
        t=owned(db,owner,tid)
        old=db.execute('SELECT * FROM bookings WHERE session_id=? AND request_id=?',(owner,request_id)).fetchone()
        if old:
            if old['task_id']!=tid or old['slot_id']!=slot_id or old['confirmed_revision']!=revision:
                raise DomainError(409,'Confirmation key was already used for a different request.')
            return snapshot(db,owner,tid)
        require_revision(t,revision)
        if t['selected_slot_id']!=slot_id or t['status']!='awaiting_confirmation':
            raise DomainError(409,'Select and review the appointment first.')
        option=next((o for o in options(db,t) if o['slot_id']==slot_id),None)
        if option is None: raise DomainError(409,'That appointment was just taken. Resume the request to see fresh options.')
        bid='NS-'+uuid.uuid4().hex[:12].upper()
        db.execute('''INSERT INTO bookings(id,task_id,slot_id,request_id,confirmed_revision,visit_fee,created_at,session_id)
          VALUES(?,?,?,?,?,?,?,?)''',(bid,tid,slot_id,request_id,revision,option['visit_fee'],now(),owner))
        db.execute("UPDATE tasks SET status='completed',revision=revision+1,updated_at=? WHERE id=?",(now(),tid))
        audit(db,owner,tid,'booking_confirmed',{'booking_id':bid,'slot_id':slot_id})
        say(db,tid,f"Your demo booking is confirmed. Reference {bid}. It is recorded in Appointments; no real technician has been dispatched.")
        return snapshot(db,owner,tid)

def add_message(owner,tid,text,role='user'):
    with transaction() as db:
        owned(db,owner,tid)
        count=db.execute('SELECT COUNT(*) FROM messages WHERE task_id=?',(tid,)).fetchone()[0]
        if count>=300: raise DomainError(429,'Message limit reached for this request. Use Edit details or start a new request.')
        say(db,tid,text,role)
