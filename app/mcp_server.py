from urllib.parse import urlparse
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.transport_security import TransportSecuritySettings
from .config import settings
from .auth import mcp_owner
from . import service
from .schemas import Details

origin=settings.public_origin.rstrip('/')
host=urlparse(origin).netloc
mcp=FastMCP('NextStep', instructions='Repair booking assistant. Work only within the token owner workspace. Select options but never claim a booking is confirmed until the user approves it in the browser. All providers are fictional.',
    stateless_http=True,json_response=True,streamable_http_path='/',
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=True,
        allowed_hosts=[host] if settings.app_env=='production' else [host,'127.0.0.1:*','localhost:*','testserver'],
        allowed_origins=[origin] if settings.app_env=='production' else [origin,'http://127.0.0.1:*','http://localhost:*']))

def owner(ctx: Context):
    request=ctx.request_context.request
    header=request.headers.get('authorization','') if request else ''
    return mcp_owner(header[7:] if header.lower().startswith('bearer ') else '')

@mcp.tool()
def list_requests(ctx: Context) -> list[dict]:
    """List this token owner's saved requests and recorded booking statuses."""
    return service.list_tasks(owner(ctx))

@mcp.tool()
def create_request(ctx: Context, details: dict | None = None) -> dict:
    """Create a repair request. Optional details: appliance, zone, preferred_date (YYYY-MM-DD), time_preference, max_visit_fee, issue_description. Never books."""
    return service.create(owner(ctx),Details.model_validate(details or {}).model_dump(mode='json'))

@mcp.tool()
def resume_request(ctx: Context, task_id: str) -> dict:
    """Resume an owned task and recheck availability. Does not reserve a slot."""
    return service.get(owner(ctx),task_id,resume=True)

@mcp.tool()
def update_request(ctx: Context, task_id: str, revision: int, changes: dict) -> dict:
    """Update explicitly requested preferences. Requires latest revision; invalidates any previous selection."""
    return service.update(owner(ctx),task_id,revision,changes)

@mcp.tool()
def find_appointments(ctx: Context, task_id: str) -> dict:
    """Get fresh eligible appointment options and the current request revision."""
    return service.get(owner(ctx),task_id)

@mcp.tool()
def select_appointment(ctx: Context, task_id: str, revision: int, slot_id: int) -> dict:
    """Select a matching appointment for review. The user MUST confirm in the NextStep browser; this tool cannot book."""
    result=service.select(owner(ctx),task_id,revision,slot_id)
    result['review_url']=origin+'/?task='+task_id
    return result
