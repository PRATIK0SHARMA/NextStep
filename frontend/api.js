export async function request(path, body, method='POST') {
  const response=await fetch('/api'+path,{
    method,credentials:'same-origin',headers:{'Content-Type':'application/json','X-NextStep':'1'},
    ...(body===undefined?{}:{body:JSON.stringify(body)}),signal:AbortSignal.timeout(45000),
  });
  const data=await response.json().catch(()=>({}));
  if(!response.ok){const error=new Error(typeof data.detail==='string'?data.detail:'Check your input and try again.');error.status=response.status;throw error;}
  return data;
}
