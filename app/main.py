import asyncio
import hmac
import logging
import secrets
import sqlite3
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager, closing, suppress
from urllib.parse import urlparse

from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
from pydantic import ValidationError

from .config import ROOT,settings
from . import db,auth,service,agent
from .schemas import Details,Change,Selection,Confirmation,Chat,Access
from .mcp_server import mcp

logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger('nextstep')

@asynccontextmanager
async def lifespan(app):
    settings.validate_release()
    db.initialize()
    async def refresh_slots():
        while True:
            await asyncio.sleep(3600)
            try:
                await asyncio.to_thread(db.seed)
            except sqlite3.Error:
                logger.error('scheduled_seed_failed')
    maintenance=asyncio.create_task(refresh_slots())
    try:
        async with mcp.session_manager.run():
            yield
    finally:
        maintenance.cancel()
        with suppress(asyncio.CancelledError):
            await maintenance

app=FastAPI(title='NextStep',version='1.0.0',lifespan=lifespan,
            docs_url='/docs' if settings.app_env!='production' else None,
            redoc_url=None,openapi_url='/openapi.json' if settings.app_env!='production' else None)
app.add_middleware(TrustedHostMiddleware,allowed_hosts=[urlparse(settings.public_origin).hostname,'127.0.0.1','localhost']+(['testserver'] if settings.app_env!='production' else []))
rates=defaultdict(deque)

def rate_limit(key,limit=120):
    current=time.monotonic()
    if len(rates)>10000:
        for k in list(rates):
            if not rates[k] or rates[k][-1]<current-60: del rates[k]
        if len(rates)>10000: raise service.DomainError(429,'Service busy; please retry later.')
    q=rates[key]
    while q and q[0]<current-60:q.popleft()
    if len(q)>=limit:raise service.DomainError(429,'Too many requests. Please wait one minute.')
    q.append(current)

@app.exception_handler(service.DomainError)
async def domain_error(request,exc):
    return JSONResponse({'detail':exc.message},status_code=exc.status)

@app.exception_handler(ValidationError)
async def validation_error(request,exc):
    # Do not echo user content or provider responses into errors.
    return JSONResponse({'detail':'Invalid preferences. Check the appliance, zone, budget, and next-14-day date.'},status_code=422)

@app.exception_handler(sqlite3.OperationalError)
async def database_busy(request,exc):
    logger.error('database_operation_failed')
    return JSONResponse({'detail':'Storage is temporarily unavailable. Please retry.'},status_code=503)

@app.middleware('http')
async def protection(request: Request,call_next):
    rid=secrets.token_hex(8);start=time.monotonic()
    try:
        if request.url.path.startswith(('/api','/mcp')):
            origin=request.headers.get('origin')
            allowed={settings.public_origin.rstrip('/')}
            if settings.app_env!='production':allowed.update({'http://127.0.0.1:8000','http://localhost:8000','http://testserver'})
            if origin and origin not in allowed:raise service.DomainError(403,'Origin not allowed')
            if request.method not in {'GET','HEAD','OPTIONS'}:
                if request.url.path.startswith('/api') and request.headers.get('x-nextstep')!='1':
                    raise service.DomainError(403,'Missing request verification header')
                chunks=[];size=0
                async for chunk in request.stream():
                    size+=len(chunk)
                    if size>32768:raise service.DomainError(413,'Request body is too large')
                    chunks.append(chunk)
                request._body=b''.join(chunks)
            key=auth.digest(request.cookies.get(auth.COOKIE,'') or (request.client.host if request.client else 'unknown'))
            rate_limit(key)
            if request.url.path=='/api/session' and request.method=='POST':rate_limit('login:'+key,10)
            if request.url.path.endswith('/messages'):rate_limit('chat:'+key,20)
            if request.url.path.startswith('/mcp'):
                value=request.headers.get('authorization','')
                auth.mcp_owner(value[7:] if value.lower().startswith('bearer ') else '')
        response=await call_next(request)
    except service.DomainError as exc:
        response=JSONResponse({'detail':exc.message},status_code=exc.status)
    response.headers['X-Request-ID']=rid
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Referrer-Policy']='same-origin'
    response.headers['X-Frame-Options']='DENY'
    response.headers['Permissions-Policy']='camera=(), geolocation=()'
    response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    if request.url.path=='/docs' and settings.app_env!='production':
        response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' https://fastapi.tiangolo.com; frame-ancestors 'none'"
    if request.url.path.startswith(('/api','/mcp')):response.headers['Cache-Control']='no-store'
    if settings.app_env=='production':response.headers['Strict-Transport-Security']='max-age=31536000'
    logger.info('request id=%s method=%s status=%s ms=%.0f',rid,request.method,response.status_code,(time.monotonic()-start)*1000)
    return response

def owner(request: Request):
    return auth.session_owner(request.cookies.get(auth.COOKIE))

@app.get('/health')
def health():
    with closing(db.connect()) as conn:conn.execute('SELECT 1')
    return {'status':'ok','service':'nextstep','version':'1.0.0'}

@app.get('/api/config')
def config():
    return {'mode':settings.llm_provider,'access_required':bool(settings.access_code),
            'today':db.today().isoformat(),'timezone':'Asia/Kolkata','fictional_providers':True}

@app.post('/api/session')
def session(body:Access,request:Request):
    try:
        sid=auth.session_owner(request.cookies.get(auth.COOKIE))
        return {'authenticated':True,'workspace':sid[:8]}
    except service.DomainError:pass
    if settings.access_code and not hmac.compare_digest(body.access_code,settings.access_code):
        raise service.DomainError(401,'Enter the workspace access code.')
    sid,token=auth.new_session()
    response=JSONResponse({'authenticated':True,'workspace':sid[:8]})
    response.set_cookie(auth.COOKIE,token,max_age=settings.session_days*86400,httponly=True,
                        secure=settings.app_env=='production',samesite='strict',path='/')
    return response

@app.get('/api/session')
def current_session(sid=Depends(owner)):
    return {'authenticated':True,'workspace':sid[:8]}

@app.get('/api/tasks')
def tasks(sid=Depends(owner)):return service.list_tasks(sid)

@app.post('/api/tasks',status_code=201)
def create_task(body:Details,sid=Depends(owner)):
    return service.create(sid,body.model_dump(mode='json'))

@app.get('/api/tasks/{tid}')
def get_task(tid:str,sid=Depends(owner)):return service.get(sid,tid)

@app.post('/api/tasks/{tid}/resume')
def resume(tid:str,sid=Depends(owner)):return service.get(sid,tid,resume=True)

@app.patch('/api/tasks/{tid}')
def update_task(tid:str,body:Change,sid=Depends(owner)):
    return service.update(sid,tid,body.revision,body.model_dump(mode='json',exclude_unset=True,exclude={'revision'}))

@app.get('/api/tasks/{tid}/options')
def get_options(tid:str,sid=Depends(owner)):return service.get(sid,tid)['options']

@app.post('/api/tasks/{tid}/select')
def select_task(tid:str,body:Selection,sid=Depends(owner)):
    return service.select(sid,tid,body.revision,body.slot_id)

@app.post('/api/tasks/{tid}/confirm')
def confirm_task(tid:str,body:Confirmation,sid=Depends(owner)):
    return service.confirm(sid,tid,body.revision,body.slot_id,body.request_id)

@app.post('/api/tasks/{tid}/messages')
async def chat(tid:str,body:Chat,sid=Depends(owner)):
    return await agent.handle(sid,tid,body.text,body.revision)

@app.post('/api/mcp-token')
def mint_token(sid=Depends(owner)):return auth.mint(sid)

@app.delete('/api/mcp-token')
def revoke_token(sid=Depends(owner)):
    with db.transaction() as conn:conn.execute('DELETE FROM mcp_tokens WHERE session_id=?',(sid,))
    return {'revoked':True}

app.mount('/mcp',mcp.streamable_http_app())
app.mount('/assets',StaticFiles(directory=ROOT/'frontend'),name='assets')

@app.get('/')
def index():return FileResponse(ROOT/'frontend'/'index.html')

@app.get('/favicon.ico',include_in_schema=False)
def favicon():return FileResponse(ROOT/'frontend'/'favicon.svg',media_type='image/svg+xml')
