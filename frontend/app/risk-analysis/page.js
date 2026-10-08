 "use client";
import {useEffect,useState} from "react";
import Shell from "../../components/Shell";
import {getJSON} from "../../lib/api";
export default function Risk(){
 const [id,setId]=useState("EMP-1001"),[data,setData]=useState(null),[error,setError]=useState("");
 async function load(){try{setError("");setData(await getJSON(`/risk/${id}`))}catch(e){setError(e.message)}}
 useEffect(()=>{load()},[]);
 return <Shell title="Risk Analysis">
  <div className="card">
   <div className="section-title">Employee Risk Score</div>
   <input value={id} onChange={e=>setId(e.target.value)} placeholder="Employee ID"/>
   <button className="btn" onClick={load}>Calculate Risk</button>
   {error && <p className="danger">{error}</p>}
   {data && <div style={{marginTop:25}}>
    <div className="muted">{data.employee_id} · Risk Category</div>
    <div className="score">{data.risk_score}</div>
    <span className={`badge ${data.risk_category}`}>{data.risk_category}</span>
    <h3>Risk Factors</h3>
    {Object.entries(data.factor_scores).map(([k,v])=><div className="factor" key={k}><div className="factor-row"><span>{k.replaceAll("_"," ")}</span><b>{v}</b></div><div className="bar"><div className="fill" style={{width:`${v}%`}}/></div></div>)}
   </div>}
  </div>
 </Shell>
}