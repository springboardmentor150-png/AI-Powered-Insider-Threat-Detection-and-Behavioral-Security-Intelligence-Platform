import Shell from "../components/Shell";
import Link from "next/link";
export default function Home(){
 return <Shell title="M3 Security Dashboard">
   <div className="cards">
    <div className="card"><div className="label">Risk Scoring</div><div className="value">0–100</div><div className="muted">Weighted employee risk</div></div>
    <div className="card"><div className="label">UEBA</div><div className="value">Peer</div><div className="muted">Comparison & trends</div></div>
    <div className="card"><div className="label">Investigation</div><div className="value">3</div><div className="muted">Demo incidents</div></div>
    <div className="card"><div className="label">Alerts</div><div className="value">3</div><div className="muted">Demo security alerts</div></div>
   </div>
   <div className="grid">
    <div className="card"><div className="section-title">M3 Workflow</div>
      <p>Risk Scoring → UEBA → Threat Investigation → Alert Management → Security Dashboards</p>
      <Link className="btn" href="/risk-analysis">Open Risk Analysis</Link>
    </div>
    <div className="card"><div className="section-title">Quick Links</div>
      <p><Link href="/incidents">View Incidents</Link></p>
      <p><Link href="/alerts">Manage Alerts</Link></p>
      <p><Link href="/ueba">Open UEBA</Link></p>
    </div>
   </div>
 </Shell>
}