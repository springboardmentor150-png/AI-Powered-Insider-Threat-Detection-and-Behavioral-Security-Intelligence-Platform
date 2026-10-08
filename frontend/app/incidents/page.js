 "use client";
import {useEffect,useState} from "react"; import Shell from "../../components/Shell"; import {getJSON,sendJSON} from "../../lib/api";
export default function Incidents(){
 const [items,setItems]=useState([]),[msg,setMsg]=useState("");
 async function load(){setItems(await getJSON("/investigation/incidents"))}
 useEffect(()=>{load()},[]);
 async function create(){try{await sendJSON("/investigation/incidents/create-from-risk/EMP-1001");setMsg("Incident created successfully");load()}catch(e){setMsg(e.message)}}
 return <Shell title="Threat Investigation"><div className="card"><button className="btn" onClick={create}>Create Incident from EMP-1001 Risk</button>{msg&&<p>{msg}</p>}</div><div className="card" style={{marginTop:20}}><table className="table"><thead><tr><th>ID</th><th>Employee</th><th>Severity</th><th>Status</th><th>Timeline</th></tr></thead><tbody>{items.map(i=><tr key={i.id}><td>#{i.id}</td><td>{i.employee_id}</td><td><span className={`badge ${i.severity}`}>{i.severity}</span></td><td>{i.status}</td><td><a href={`/incidents/${i.id}`}>View</a></td></tr>)}</tbody></table></div></Shell>
}