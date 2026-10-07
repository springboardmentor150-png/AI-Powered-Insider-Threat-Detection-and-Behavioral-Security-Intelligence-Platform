import Sidebar from "./Sidebar";
export default function Shell({children,title}){
 return <div className="app"><Sidebar/><main className="main"><div className="top"><div><div className="title">{title}</div><div className="muted">Insider Threat Behavioral Intelligence System</div></div><span className="badge high">Security Analyst</span></div>{children}</main></div>
}