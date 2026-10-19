from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict


# ==================== AUTH / USER SCHEMAS ====================

class UserCreate(BaseModel):
    email: str
    password: str
    role: str = "security_analyst"


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class SignupResponse(BaseModel):
    message: str
    id: int
    email: str
    role: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ==================== EMPLOYEE SCHEMAS ====================

class EmployeeCreate(BaseModel):
    employee_id: str
    name: str
    email: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    manager_name: Optional[str] = None
    manager_id: Optional[int] = None
    employment_type: Optional[str] = "Full-time"
    work_location: Optional[str] = "Hyderabad"
    joining_date: Optional[str] = "2022-01-15"
    years_of_experience: Optional[int] = 5
    education: Optional[str] = "B.Tech Computer Science"
    previous_role: Optional[str] = None
    skills: Optional[str] = None
    professional_summary: Optional[str] = None
    device_info: Optional[str] = None
    access_privileges: Optional[str] = "STANDARD"
    risk_score: Optional[int] = 0
    risk_level: Optional[str] = None
    status: Optional[str] = "ACTIVE"


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    manager_name: Optional[str] = None
    manager_id: Optional[int] = None
    employment_type: Optional[str] = None
    work_location: Optional[str] = None
    joining_date: Optional[str] = None
    years_of_experience: Optional[int] = None
    education: Optional[str] = None
    previous_role: Optional[str] = None
    skills: Optional[str] = None
    professional_summary: Optional[str] = None
    device_info: Optional[str] = None
    access_privileges: Optional[str] = None
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    status: Optional[str] = None


class EmployeeResponse(BaseModel):
    id: int
    employee_id: str
    name: str
    email: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    manager_name: Optional[str] = None
    manager_id: Optional[int] = None
    employment_type: Optional[str] = "Full-time"
    work_location: Optional[str] = "Hyderabad"
    joining_date: Optional[str] = "2022-01-15"
    years_of_experience: Optional[int] = 5
    education: Optional[str] = "B.Tech Computer Science"
    previous_role: Optional[str] = None
    skills: Optional[str] = None
    professional_summary: Optional[str] = None
    device_info: Optional[str] = None
    access_privileges: Optional[str] = None
    risk_score: int
    risk_level: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedEmployeesResponse(BaseModel):
    items: List[EmployeeResponse]
    page: int
    limit: int
    total: int


class EmployeeDetailResponse(BaseModel):
    employee: EmployeeResponse
    alerts: List[Any] = []
    incidents: List[Any] = []
    recent_activities: List[Any] = []
    baseline: Optional[Any] = None
    risk_history: List[Any] = []



# ==================== MONGODB ACTIVITY LOG SCHEMAS ====================

class ActivityIngestRequest(BaseModel):
    employee_id: str
    event_type: str
    action: Optional[str] = None
    resource: Optional[str] = None
    timestamp: Optional[str] = None
    device: Optional[str] = None
    ip_address: Optional[str] = None
    location: Optional[str] = None
    risk_weight: Optional[int] = 0
    is_suspicious: Optional[bool] = False
    anomaly_reasons: Optional[List[str]] = []
    is_test_event: Optional[bool] = False
    details: Optional[Dict[str, Any]] = {}


class TestActivityCreate(BaseModel):
    employee_id: str
    activity_type: str
    action: str
    resource: str
    scenario: str
    download_size_mb: Optional[int] = 0
    device_id: Optional[str] = None
    ip_address: Optional[str] = None



class MongoActivityItem(BaseModel):
    id: str
    employee_id: str
    event_type: str
    action: Optional[str] = None
    resource: Optional[str] = None
    timestamp: str
    device: Optional[str] = None
    ip_address: Optional[str] = None
    location: Optional[str] = None
    risk_weight: int = 0
    is_suspicious: bool = False
    anomaly_reasons: List[str] = []
    is_test_event: bool = False
    details: Dict[str, Any] = {}


class PaginatedMongoActivityResponse(BaseModel):
    items: List[MongoActivityItem]
    page: int
    limit: int
    total: int


class TimelinePoint(BaseModel):
    time: str
    total_events: int
    suspicious_events: int
    max_risk_weight: int
    sample_event: Optional[str] = None
    sample_device: Optional[str] = None
    sample_employee: Optional[str] = None


class TimelineEventItem(BaseModel):
    id: str
    employee_id: str
    event_type: str
    action: Optional[str] = None
    resource: Optional[str] = None
    timestamp: str
    device: Optional[str] = None
    ip_address: Optional[str] = None
    location: Optional[str] = None
    risk_weight: int = 0
    severity: str = "LOW"
    is_suspicious: bool = False
    is_anomalous: bool = False
    is_anomaly: bool = False
    anomaly_reasons: List[str] = []
    reason: Optional[str] = None
    why_suspicious: Optional[str] = None
    is_test_event: bool = False
    details: Dict[str, Any] = {}



class ActivityTimelineResponse(BaseModel):
    items: List[TimelineEventItem]
    total: int


class HeatmapCell(BaseModel):
    day: str
    day_index: int
    hour: int
    hour_label: str
    event_count: int
    suspicious_count: int
    is_off_hours: bool
    primary_event: Optional[str] = None


class EventTypeDistributionItem(BaseModel):
    event_type: str
    label: str
    count: int
    percentage: float


class EmployeeActivityProfile(BaseModel):
    employee_id: str
    typical_login_time: str
    typical_logout_time: str
    known_devices: List[str]
    known_ips: List[str]
    average_daily_events: int
    most_common_event_type: str
    total_downloads_mb: float
    off_hours_percentage: float
    total_events: int
    suspicious_events: int


# ==================== BEHAVIORAL BASELINE SCHEMAS ====================

class BehavioralBaselineResponse(BaseModel):
    id: int
    employee_id: int
    employee_identifier: Optional[str] = None
    employee_name: Optional[str] = None
    normal_start_hour: int
    normal_end_hour: int
    usual_devices: Optional[str] = None
    usual_ips: Optional[str] = None
    usual_resources: Optional[str] = None
    usual_download_limit_mb: int
    total_activities_sampled: int
    last_baseline_update: datetime
    status_message: str

    model_config = ConfigDict(from_attributes=True)


class DetectedAnomalySignal(BaseModel):
    anomaly_type: str
    severity: str
    description: str
    risk_contribution: int
    observed_value: str
    expected_baseline: str


class BehaviorAnalysisResponse(BaseModel):
    employee: EmployeeResponse
    baseline: Optional[BehavioralBaselineResponse] = None
    has_sufficient_history: bool
    status_summary: str
    recent_anomalies: List[DetectedAnomalySignal]
    total_anomalies_detected: int
    behavior_deviation_score: int
    individual_metrics: Optional[Dict[str, Any]] = None
    peer_comparison: Optional[Dict[str, Any]] = None
    trend_analysis: Optional[Dict[str, Any]] = None
    entity_analytics: Optional[Dict[str, Any]] = None
    threat_prediction: Optional[Dict[str, Any]] = None


# ==================== RISK SCORE SCHEMAS ====================

class RiskScoreHistoryResponse(BaseModel):
    id: int
    employee_id: int
    score: int
    risk_level: str
    contributing_factors: Optional[str] = None
    calculated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EmployeeRiskItem(BaseModel):
    employee_id: str
    name: str
    department: Optional[str] = None
    risk_score: int
    risk_level: str
    status: str
    top_factor: Optional[str] = None
    last_calculated: datetime


class PaginatedRiskScoresResponse(BaseModel):
    items: List[EmployeeRiskItem]
    total: int


# ==================== ALERT SCHEMAS ====================

class AlertCreate(BaseModel):
    employee_id: int
    title: str
    message: str
    category: Optional[str] = "DATA_EXFILTRATION"
    severity: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    status: Optional[str] = "OPEN"
    risk_score: Optional[int] = 0
    assigned_to: Optional[int] = None


class AlertResponse(BaseModel):
    id: int
    employee_id: int
    employee_name: Optional[str] = None
    employee_identifier: Optional[str] = None
    title: str
    message: str
    category: str
    severity: str
    status: str
    risk_score: int
    assigned_to: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedAlertsResponse(BaseModel):
    items: List[AlertResponse]
    page: int
    limit: int
    total: int


# ==================== INCIDENT SCHEMAS ====================

class IncidentCreate(BaseModel):
    employee_id: int
    alert_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    severity: Optional[str] = "HIGH"


class IncidentStatusUpdate(BaseModel):
    status: str  # OPEN, INVESTIGATING, CONTAINED, RESOLVED, CLOSED
    resolution_notes: Optional[str] = None


class IncidentResponse(BaseModel):
    id: int
    employee_id: int
    employee_name: Optional[str] = None
    employee_identifier: Optional[str] = None
    alert_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    status: str
    severity: str
    assigned_to: Optional[int] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedIncidentsResponse(BaseModel):
    items: List[IncidentResponse]
    page: int
    limit: int
    total: int


# ==================== INVESTIGATION CENTER SCHEMAS ====================

class InvestigationNoteCreate(BaseModel):
    note_text: str
    incident_id: Optional[int] = None


class InvestigationNoteResponse(BaseModel):
    id: int
    employee_id: int
    incident_id: Optional[int] = None
    author_email: str
    note_text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvestigationTimelineItem(BaseModel):
    id: str
    timestamp: str
    event_type: str
    source: str  # "TELEMETRY", "ANOMALY", "RISK_CHANGE", "ALERT", "INCIDENT", "ANALYST_NOTE"
    title: str
    description: str
    severity: str
    employee_id: str
    risk_impact: Optional[int] = None
    related_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class FullInvestigationDossier(BaseModel):
    employee: EmployeeResponse
    activity_profile: EmployeeActivityProfile
    active_alerts: List[AlertResponse]
    active_incidents: List[IncidentResponse]
    risk_history: List[RiskScoreHistoryResponse]
    notes: List[InvestigationNoteResponse]
    timeline: List[InvestigationTimelineItem]


# ==================== GLOBAL SEARCH SCHEMAS ====================

class SearchMatchItem(BaseModel):
    category: str  # "EMPLOYEE", "ALERT", "INCIDENT", "ACTIVITY"
    id: str
    title: str
    subtitle: str
    severity: Optional[str] = None
    link: str


class GlobalSearchResponse(BaseModel):
    query: str
    results: List[SearchMatchItem]
    total_matches: int


# ==================== AUDIT LOG & NOTIFICATIONS SCHEMAS ====================

class AuditLogResponse(BaseModel):
    id: int
    user_email: str
    action: str
    target_type: str
    target_id: Optional[str] = None
    details: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    title: str
    message: str
    alert_id: Optional[int] = None
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== REPORT & DASHBOARD SCHEMAS ====================

class ThreatCategoryCount(BaseModel):
    category: str
    count: int
    percentage: float


class ReportSummaryResponse(BaseModel):
    generated_at: datetime
    total_monitored_employees: int
    high_risk_employee_count: int
    total_alerts_period: int
    critical_alerts_period: int
    total_incidents_period: int
    resolved_incidents_period: int
    top_threat_categories: List[ThreatCategoryCount]
    highest_risk_employees: List[EmployeeResponse]


class DashboardSummaryResponse(BaseModel):
    total_employees: int
    active_employees: int
    high_risk_count: int
    critical_risk_count: int
    total_alerts: int
    open_alerts: int
    investigating_alerts: int
    total_incidents: int
    open_incidents: int
    avg_risk_score: float
    total_activities_ingested: int


class DashboardTrendPoint(BaseModel):
    date: str
    avg_risk: float
    alert_count: int


class DashboardTrendResponse(BaseModel):
    points: List[DashboardTrendPoint]


class ThreatDistributionResponse(BaseModel):
    categories: List[ThreatCategoryCount]


# ==================== SYSTEM SETTING SCHEMAS ====================

class SystemSettingResponse(BaseModel):
    id: int
    key: str
    value: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SystemSettingsUpdate(BaseModel):
    settings: Dict[str, str]


# ==================== COMBINED ANOMALY REPORT SCHEMAS (DAYS 19-20) ====================

class RuleAnomalyReportItem(BaseModel):
    id: Optional[str] = None
    employee_id: str
    anomaly_type: str
    indicator: str
    severity: str
    observed_value: Any
    typical_value: Optional[Any] = None
    expected_baseline: Optional[Any] = None
    deviation_ratio: Optional[float] = None
    detection_timestamp: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class MLAnomalyReportItem(BaseModel):
    id: Optional[str] = None
    employee_id: str
    anomaly_type: str = "ML_ISOLATION_FOREST"
    indicator: str = "isolation_forest"
    anomaly_score: float
    anomaly_flag: int = -1
    date: Optional[str] = None
    detection_timestamp: Optional[str] = None
    observed_value: Optional[Any] = None
    expected_baseline: Optional[str] = None
    feature_values: Optional[Dict[str, Any]] = None
    details: Optional[Dict[str, Any]] = None


class EmployeeAnomalyReportResponse(BaseModel):
    employee_id: str
    employee_name: Optional[str] = None
    department: Optional[str] = None
    total_flags: int = 0
    total_anomalies: int = 0
    total_rule_anomalies: int = 0
    total_ml_anomalies: int = 0
    severity_counts: Dict[str, int]
    rule_based_anomalies: List[Dict[str, Any]]
    ml_anomalies: List[Dict[str, Any]]


class TopEmployeeAnomalyItem(BaseModel):
    employee_id: str
    employee_name: Optional[str] = None
    department: Optional[str] = None
    total_anomalies: int = 0
    rule_anomalies: int = 0
    ml_anomalies: int = 0
    anomaly_count: Optional[int] = None
    highest_severity: Optional[str] = None


class DailyAnomalyCountItem(BaseModel):
    date: str
    total: int
    rule_count: int
    ml_count: int


class AnomalySummaryResponse(BaseModel):
    total_anomalies: int
    total_rule_anomalies: int
    total_ml_anomalies: int
    unique_employees: int
    counts_by_severity: Dict[str, int]
    top_employees: List[TopEmployeeAnomalyItem]
    top_10_employees: Optional[List[TopEmployeeAnomalyItem]] = None
    anomalies_over_time: List[DailyAnomalyCountItem]


# ==================== MILESTONE 3: RISK SCORING & UEBA SCHEMAS ====================

class RiskScoreResponse(BaseModel):
    employee_id: str
    sub_scores: Dict[str, float]
    final_score: float
    risk_level: str


class PeerGroupComparisonResponse(BaseModel):
    employee_id: str
    employee_score: float
    peer_count: int
    department: Optional[str] = None
    department_avg_score: Optional[float] = None
    deviation_from_peers: Optional[float] = None
    peer_percentile: Optional[float] = None
    note: Optional[str] = None


class TrendDirectionResponse(BaseModel):
    employee_id: str
    first_week_avg: float
    second_week_avg: float
    direction: str


class UEBAProfileResponse(BaseModel):
    employee_id: str
    employee_name: Optional[str] = None
    department: Optional[str] = None
    risk_score: Dict[str, Any]
    peer_comparison: Dict[str, Any]
    trend: Dict[str, Any]


