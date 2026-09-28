"use client";

import { useState } from "react";

export default function SettingsPage() {
  const [platformName, setPlatformName] = useState("ITBIS");
  const [sessionDuration, setSessionDuration] = useState("8 Hours");
  const [notifications, setNotifications] = useState(true);
  const [saved, setSaved] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();

    setSaved(true);

    setTimeout(() => {
      setSaved(false);
    }, 3000);
  };

  return (
    <main className="settings-page">

      {/* Header */}
      <div className="settings-header">
        <div>
          <h1>Platform Settings</h1>
          <p>
            Configure security and platform preferences
          </p>
        </div>

        <div className="settings-status">
          <span className="settings-status-dot"></span>
          System Secure
        </div>
      </div>

      {/* Settings Layout */}
      <div className="settings-layout">

        {/* Sidebar */}
        <aside className="settings-sidebar">

          <div className="settings-nav active">
            <span>🛡️</span>
            Security Settings
          </div>

          <div className="settings-nav">
            <span>🔔</span>
            Notifications
          </div>

          <div className="settings-nav">
            <span>👤</span>
            Account
          </div>

        </aside>

        {/* Main Settings */}
        <section className="settings-content">

          <div className="settings-card">

            <div className="settings-card-header">
              <div className="settings-card-icon">
                🛡️
              </div>

              <div>
                <h2>Security Settings</h2>
                <p>
                  Manage core security and session configuration
                </p>
              </div>
            </div>

            <form onSubmit={handleSave}>

              {/* Platform Name */}
              <div className="setting-field">

                <label>Platform Name</label>

                <input
                  type="text"
                  value={platformName}
                  onChange={(e) =>
                    setPlatformName(e.target.value)
                  }
                  placeholder="Enter platform name"
                />

                <span className="field-help">
                  Name displayed across the security platform
                </span>

              </div>

              {/* Session Duration */}
              <div className="setting-field">

                <label>Session Duration</label>

                <select
                  value={sessionDuration}
                  onChange={(e) =>
                    setSessionDuration(e.target.value)
                  }
                >
                  <option>8 Hours</option>
                  <option>12 Hours</option>
                  <option>24 Hours</option>
                </select>

                <span className="field-help">
                  Controls how long a user session remains active
                </span>

              </div>

              {/* Notifications */}
              <div className="notification-setting">

                <div>
                  <strong>
                    Enable Security Notifications
                  </strong>

                  <p>
                    Receive notifications when suspicious
                    security events are detected.
                  </p>
                </div>

                <label className="toggle">

                  <input
                    type="checkbox"
                    checked={notifications}
                    onChange={(e) =>
                      setNotifications(e.target.checked)
                    }
                  />

                  <span className="slider"></span>

                </label>

              </div>

              {/* Save */}
              <div className="settings-actions">

                {saved && (
                  <span className="save-success">
                    ✓ Settings saved successfully
                  </span>
                )}

                <button
                  type="submit"
                  className="save-settings-btn"
                >
                  Save Settings
                </button>

              </div>

            </form>

          </div>

          {/* Security Information */}
          <div className="security-info-card">

            <div className="info-icon">
              🔐
            </div>

            <div>
              <h3>Security Configuration</h3>

              <p>
                ITBIS security settings help protect platform
                access and provide timely notifications for
                suspicious activities.
              </p>

              <div className="security-items">

                <span>✓ Secure Authentication</span>
                <span>✓ Role-Based Access Control</span>
                <span>✓ Security Monitoring</span>

              </div>
            </div>

          </div>

        </section>

      </div>

    </main>
  );
}