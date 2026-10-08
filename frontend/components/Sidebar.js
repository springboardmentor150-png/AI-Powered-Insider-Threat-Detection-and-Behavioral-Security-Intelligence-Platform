import Link from "next/link";
export default function Sidebar(){
  return <aside className="sidebar">
    <div className="brand">ITBIS Security</div>
    <div className="sub">Milestone 3 · Risk Intelligence</div>
    <nav className="nav">
      <Link href="/">Dashboard</Link>
      <Link href="/risk-analysis">Risk Analysis</Link>
      <Link href="/incidents">Incidents</Link>
      <Link href="/alerts">Alerts</Link>
      <Link href="/ueba">UEBA</Link>
      <Link href="/soc-dashboard">SOC Dashboard</Link>
      <Link href="/manager-dashboard">Manager Dashboard</Link>
    </nav>
  </aside>
}