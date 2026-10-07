const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
export async function getJSON(path){
  const res = await fetch(`${API}${path}`, {cache:"no-store"});
  if(!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}
export async function sendJSON(path, method="POST"){
  const res = await fetch(`${API}${path}`, {method, headers:{"Content-Type":"application/json"}});
  if(!res.ok) {
    let d={}; try{d=await res.json()}catch{}
    throw new Error(d.detail || `API error ${res.status}`);
  }
  return res.json();
}
