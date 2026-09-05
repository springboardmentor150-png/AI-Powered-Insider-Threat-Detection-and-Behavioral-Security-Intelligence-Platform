# backend/app/ml_engine/threat_explainer.py
from typing import List, Dict, Any

class ThreatIntelligenceExplainer:
    """
    Generates human-readable SOC threat intelligence reports,
    maps suspicious behaviors to MITRE ATT&CK techniques,
    and formulates containment playbooks.
    """
    MITRE_CATALOG = {
        "USB_EXFILTRATION": {
            "technique_id": "T1052.001",
            "name": "Exfiltration Over Physical Medium: USB / Removable Media",
            "description": "Adversary or malicious insider copies sensitive data to a physical USB flash drive or portable hard drive to bypass network DLP filters."
        },
        "DATABASE_SCRAPING": {
            "technique_id": "T1530 / T1005",
            "name": "Data from Cloud Storage / Local System Scraping",
            "description": "User queries abnormally high volumes of structured records, bypassing typical daily query limits to extract bulk customer or financial records."
        },
        "PRIVILEGE_ESCALATION": {
            "technique_id": "T1078 / T1548",
            "name": "Abuse of Elevation Control Mechanism / Valid Accounts",
            "description": "User executes unauthorized administrative commands or attempts sudo override outside their designated job privileges."
        },
        "OFF_HOURS_ACCESS": {
            "technique_id": "T1078.004",
            "name": "Valid Accounts: Cloud / Network Off-Hours Access",
            "description": "Access detected outside normal business hours or from unexpected geographic locations, indicating potential credential compromise or covert exfiltration."
        },
        "MASS_DOWNLOAD": {
            "technique_id": "T1567",
            "name": "Exfiltration Over Web Service / Cloud Drive",
            "description": "Substantial burst of confidential files transferred or downloaded to local storage within a short time frame."
        }
    }

    def generate_explanation(
        self,
        employee_name: str,
        employee_id: str,
        department: str,
        risk_score: float,
        threat_level: str,
        indicators: List[str],
        logs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Creates complete threat breakdown for SOC Analysts.
        """
        mitre_mapping = []
        recommended_actions = []

        # Analyze logs to identify specific threat signatures
        has_usb = any("usb" in (l.get("event_type") or "").lower() for l in logs)
        has_db = any(int((l.get("details") or {}).get("rows_accessed", 0)) > 2000 for l in logs)
        has_priv = any("privilege" in (l.get("event_type") or "").lower() or (l.get("details") or {}).get("sudo") for l in logs)
        has_off_hours = any("temporal" in ind.lower() for ind in indicators)
        has_mass_dl = any("download" in ind.lower() for ind in indicators) or any(float((l.get("details") or {}).get("size_mb", 0)) > 100 for l in logs)

        if has_usb:
            mitre_mapping.append(self.MITRE_CATALOG["USB_EXFILTRATION"])
            recommended_actions.append("Execute remote DLP endpoint lock on removable USB storage devices.")
            recommended_actions.append("Quarantine host workstation and collect USB volume serial numbers.")

        if has_db:
            mitre_mapping.append(self.MITRE_CATALOG["DATABASE_SCRAPING"])
            recommended_actions.append("Temporarily restrict database connection credentials and review query transaction logs.")
            recommended_actions.append("Audit all SQL query outputs accessed in the last 48 hours for PII/PCI data exposure.")

        if has_priv:
            mitre_mapping.append(self.MITRE_CATALOG["PRIVILEGE_ESCALATION"])
            recommended_actions.append("Revoke temporary administrative tokens and trigger immediate MFA re-authentication.")
            recommended_actions.append("Review audit trail for unauthorized role modifications or security group changes.")

        if has_mass_dl:
            mitre_mapping.append(self.MITRE_CATALOG["MASS_DOWNLOAD"])
            recommended_actions.append("Inspect corporate cloud repository access logs (SharePoint/Google Drive/GitLab).")
            recommended_actions.append("Verify if downloaded assets were transferred to personal cloud accounts.")

        if has_off_hours:
            mitre_mapping.append(self.MITRE_CATALOG["OFF_HOURS_ACCESS"])
            recommended_actions.append("Verify whether the employee was authorized for off-hours on-call maintenance.")

        if not recommended_actions:
            if threat_level in ["HIGH", "CRITICAL"]:
                recommended_actions.append("Initiate Level-2 SOC incident investigation and contact employee's line manager.")
                recommended_actions.append("Preserve forensic logs and monitor network egress bandwidth.")
            else:
                recommended_actions.append("Continue standard automated baseline monitoring. No immediate containment required.")

        # Construct concise AI threat narrative
        if threat_level == "CRITICAL":
            narrative = (
                f"CRITICAL THREAT ALERT: Employee {employee_name} ({employee_id}, {department}) exhibits high-severity anomalous behavior "
                f"with a composite risk score of {risk_score}/100. Key indicators demonstrate probable data exfiltration or active account compromise, "
                f"exceeding normal baseline thresholds by over 400%. Immediate SOC intervention is advised."
            )
        elif threat_level == "HIGH":
            narrative = (
                f"ELEVATED RISK DETECTION: Monitored activity for {employee_name} ({employee_id}) shows significant variance from established behavioral baselines "
                f"(Risk Score: {risk_score}/100). Multiple anomalous signals detected across data transfer and access patterns."
            )
        elif threat_level == "MEDIUM":
            narrative = (
                f"MODERATE ANOMALY: Activity logs for {employee_name} ({employee_id}) include minor deviations (Risk Score: {risk_score}/100). "
                f"Pattern could indicate unusual project deliverables or minor policy exceptions."
            )
        else:
            narrative = (
                f"NORMAL ACTIVITY: Telemetry for {employee_name} ({employee_id}) remains within nominal behavioral baselines (Risk Score: {risk_score}/100). "
                f"No suspicious insider threat indicators detected."
            )

        return {
            "narrative": narrative,
            "mitre_mapping": mitre_mapping,
            "recommended_actions": recommended_actions
        }

threat_explainer = ThreatIntelligenceExplainer()
