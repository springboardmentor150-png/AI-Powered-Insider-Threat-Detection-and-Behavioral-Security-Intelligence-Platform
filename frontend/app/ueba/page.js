 "use client";
import {useState} from "react"; import Shell from "../../components/Shell"; import {getJSON} from "../../lib/api";
export default function Ueba(){
 const [id,setId]=useState("EMP-1001"),[peer,setPeer]=useState(null),[trend,setTrend]=useState(null);
 async function load(){setPeer(await getJSON(`/ueba/peer/${id}`));setTrend(await getJSON(`/ueba/trend/${id}`))}
 return <Shell title="UEBA Intelligence"><div className="card"><input value={id} onChange={e=>setId(e.target.value)}/><button className="btn" onClick={load}>Analyze Employee</button></div>
 {peer&&<div className="cards" style={{marginTop:20}}>{["employee_score","department_avg_score","deviation_from_peers","peer_count"].map(k=><div className="card" key={k}><div className="label">{k.replaceAll("_"," ")}</div><div className="value">{peer[k] ?? "—"}</div></div>)}</div>}
 {peer?.note&&<div className="card" style={{marginTop:20}}><b>{peer.note}</b></div>}
 {trend&&<div className="card" style={{marginTop:20}}><div className="section-title">30-Day Behavioral Trend</div><div className="chart">{trend.trend.map((x,i)=><div key={i} title={`${x.date}: ${x.anomaly_count}`} className="barcol" style={{height:`${Math.max(8,x.anomaly_count*20)}px`}}/>)}</div></div>}
 </Shell>
}