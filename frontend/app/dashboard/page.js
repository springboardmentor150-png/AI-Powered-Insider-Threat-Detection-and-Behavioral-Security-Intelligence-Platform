"use client";

import Link from "next/link";

export default function DashboardPage() {
  const stats = [
    {
      title: "Total Employees",
      value: "120",
      icon: "👥",
      color: "blue",
      change: "↑ 12%",
    },
    {
      title: "Activity Logs",
      value: "1,248",
      icon: "📊",
      color: "purple",
      change: "↑ 24%",
    },
    {
      title: "Active Alerts",
      value: "08",
      icon: "🔔",
      color: "orange",
      change: "↑ 33%",
    },
    {
      title: "Open Incidents",
      value: "03",
      icon: "⚠",
      color: "red",
      change: "↓ 25%",
    },
  ];

  const activities = [
    ["EMP-1001", "Login", "10:30 AM", "Normal"],
    ["EMP-1002", "File Access", "10:15 AM", "Normal"],
    ["EMP-1003", "File Transfer", "09:50 AM", "Suspicious"],
    ["EMP-1004", "Logout", "09:30 AM", "Normal"],
  ];

  return (
    <div className="dashboard-layout">

      {/* SIDEBAR */}
      <aside className="sidebar">

        <div className="brand">
          <div className="brand-logo">IT</div>

          <div className="brand-text">
            <h2>ITBIS</h2>
            <span>Security Platform</span>
          </div>
        </div>

        <div className="menu-title">MAIN MENU</div>

        <nav className="sidebar-nav">

          <Link href="/dashboard" className="menu-item active">
            <span>⌂</span>
            Dashboard
          </Link>

          <Link href="/employees" className="menu-item">
            <span>♟</span>
            Employees
          </Link>

          <Link href="/activity-logs" className="menu-item">
            <span>▤</span>
            Activity Logs
          </Link>

          <Link href="/alerts" className="menu-item">
            <span>♟</span>
            Alerts
            <b className="menu-badge">8</b>
          </Link>

          <Link href="/incidents" className="menu-item">
            <span>⚠</span>
            Incidents
          </Link>

          <Link href="/users" className="menu-item">
            <span>♟</span>
            Users
          </Link>

          <Link href="/reports" className="menu-item">
            <span>▥</span>
            Reports
          </Link>

          <Link href="/settings" className="menu-item">
            <span>⚙</span>
            Settings
          </Link>

        </nav>

        <div className="sidebar-footer">
          <div className="secure-box">
            <span className="secure-dot"></span>

            <div>
              <strong>System Secure</strong>
              <small>All systems operational</small>
            </div>
          </div>

          <p>ITBIS v1.0</p>
        </div>

      </aside>

      {/* MAIN */}
      <main className="main-content">

        {/* TOP HEADER */}
        <header className="top-header">

          <div className="search-box">
            <span>⌕</span>
            <input
              type="text"
              placeholder="Search employees, logs, incidents..."
            />
          </div>

          <div className="header-right">

            <div className="notification">
              🔔
              <b>8</b>
            </div>

            <div className="profile-avatar">
              SA
            </div>

            <div className="profile-info">
              <strong>Security Analyst</strong>
              <span>Administrator</span>
            </div>

            <span className="profile-arrow">⌄</span>

          </div>

        </header>

        <div className="page-content">

          {/* PAGE TITLE */}
          <div className="page-title">

            <div>
              <h1>Security Dashboard</h1>
              <p>Monitor employee activities and security events.</p>
            </div>

            <div className="date-box">
              <span>▣</span>
              <div>
                <strong>24 Sep, 2026</strong>
                <small>Security Overview</small>
              </div>
            </div>

          </div>

          {/* STAT CARDS */}
          <section className="stats-grid">

            {stats.map((stat) => (
              <div className="stat-card" key={stat.title}>

                <div className={"stat-icon " + stat.color}>
                  {stat.icon}
                </div>

                <div className="stat-information">
                  <span>{stat.title}</span>
                  <h2>{stat.value}</h2>

                  <div className="stat-change">
                    <b>{stat.change}</b>
                    <small>vs. last month</small>
                  </div>
                </div>

              </div>
            ))}

          </section>

          {/* MAIN GRID */}
          <section className="main-grid">

            <div className="left-column">

              {/* WELCOME */}
              <div className="welcome-card">

                <div className="welcome-icon">
                  🛡
                </div>

                <div className="welcome-text">
                  <span>WELCOME TO ITBIS</span>

                  <h2>
                    AI-powered insider threat detection
                  </h2>

                  <p>
                    and behavioral security intelligence platform.
                  </p>
                </div>

                <Link href="/reports" className="generate-button">
                  Generate Report →
                </Link>

              </div>

              {/* ACTIVITY */}
              <div className="dashboard-card">

                <div className="card-header">

                  <div>
                    <h3>⌁ &nbsp; Recent Activity</h3>
                    <p>Latest employee activities</p>
                  </div>

                  <Link href="/activity-logs">
                    View All →
                  </Link>

                </div>

                <div className="activity-table">

                  <table>

                    <thead>
                      <tr>
                        <th>EMPLOYEE</th>
                        <th>ACTIVITY</th>
                        <th>TIME</th>
                        <th>STATUS</th>
                      </tr>
                    </thead>

                    <tbody>

                      {activities.map((activity, index) => (
                        <tr key={index}>

                          <td>
                            <div className="employee-cell">
                              <span className="activity-dot"></span>
                              {activity[0]}
                            </div>
                          </td>

                          <td>{activity[1]}</td>

                          <td>{activity[2]}</td>

                          <td>
                            <span
                              className={
                                activity[3] === "Suspicious"
                                  ? "status suspicious"
                                  : "status normal"
                              }
                            >
                              {activity[3]}
                            </span>
                          </td>

                        </tr>
                      ))}

                    </tbody>

                  </table>

                </div>

              </div>

            </div>

            {/* RIGHT COLUMN */}
            <div className="right-column">

              {/* ALERTS */}
              <div className="dashboard-card alerts-card">

                <div className="card-header">

                  <div>
                    <h3>🔔 &nbsp; Security Alerts</h3>
                    <p>Requires attention</p>
                  </div>

                  <Link href="/alerts">
                    View All →
                  </Link>

                </div>

                <div className="alert-list">

                  <div className="alert-row">
                    <div className="alert-symbol danger">!</div>

                    <div className="alert-content">
                      <strong>Suspicious File Transfer</strong>
                      <span>EMP-1003 detected unusual activity</span>
                    </div>

                    <small>10 min</small>
                  </div>

                  <div className="alert-row">
                    <div className="alert-symbol warning">!</div>

                    <div className="alert-content">
                      <strong>Multiple Login Attempts</strong>
                      <span>EMP-1010 exceeded login threshold</span>
                    </div>

                    <small>25 min</small>
                  </div>

                  <div className="alert-row">
                    <div className="alert-symbol information">i</div>

                    <div className="alert-content">
                      <strong>Unusual Login Location</strong>
                      <span>EMP-1012 login from new location</span>
                    </div>

                    <small>42 min</small>
                  </div>

                </div>

              </div>

              {/* ACTIVITY OVERVIEW */}
              <div className="dashboard-card chart-card">

                <div className="card-header">

                  <div>
                    <h3>⌁ &nbsp; Security Activity Overview</h3>
                    <p>Activity trends</p>
                  </div>

                  <div className="chart-filters">
                    <button className="selected">7D</button>
                    <button>30D</button>
                    <button>90D</button>
                  </div>

                </div>

                <div className="chart">

                  <div className="chart-y">
                    <span>200</span>
                    <span>150</span>
                    <span>100</span>
                    <span>50</span>
                    <span>0</span>
                  </div>

                  <div className="chart-area">

                    <svg
                      viewBox="0 0 500 180"
                      preserveAspectRatio="none"
                    >

                      <defs>
                        <linearGradient
                          id="areaGradient"
                          x1="0"
                          x2="0"
                          y1="0"
                          y2="1"
                        >
                          <stop
                            offset="0%"
                            stopColor="#3b82f6"
                            stopOpacity="0.25"
                          />

                          <stop
                            offset="100%"
                            stopColor="#3b82f6"
                            stopOpacity="0.02"
                          />
                        </linearGradient>
                      </defs>

                      <polygon
                        points="0,150 80,105 160,120 240,75 320,100 410,65 500,25 500,180 0,180"
                        fill="url(#areaGradient)"
                      />

                      <polyline
                        points="0,150 80,105 160,120 240,75 320,100 410,65 500,25"
                        fill="none"
                        stroke="#2563eb"
                        strokeWidth="3"
                      />

                      <circle cx="0" cy="150" r="4" fill="#2563eb" />
                      <circle cx="80" cy="105" r="4" fill="#2563eb" />
                      <circle cx="160" cy="120" r="4" fill="#2563eb" />
                      <circle cx="240" cy="75" r="4" fill="#2563eb" />
                      <circle cx="320" cy="100" r="4" fill="#2563eb" />
                      <circle cx="410" cy="65" r="4" fill="#2563eb" />
                      <circle cx="500" cy="25" r="4" fill="#2563eb" />

                    </svg>

                    <div className="chart-days">
                      <span>Sep 18</span>
                      <span>Sep 19</span>
                      <span>Sep 20</span>
                      <span>Sep 21</span>
                      <span>Sep 22</span>
                      <span>Sep 23</span>
                      <span>Sep 24</span>
                    </div>

                  </div>

                </div>

              </div>

            </div>

          </section>

        </div>

      </main>

    </div>
  );
}