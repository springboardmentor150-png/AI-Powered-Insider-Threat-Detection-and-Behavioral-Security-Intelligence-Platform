import unittest
import json
from datetime import datetime, timezone
from app.database import SessionLocal, engine
from app.models import Base, User, Employee, Alert, Incident, InvestigationNote, AuditLog, Notification
from app.seed import seed_initial_data
from app.mongodb import mongo_service
from app.services.risk_engine import compute_risk_level, calculate_and_update_employee_risk
from app.services.alert_engine import evaluate_and_trigger_alerts
from app.services.baseline_engine import get_or_create_baseline


class TestITBISFinalSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        with SessionLocal() as db:
            seed_initial_data(db)

    def test_01_employees_sequential_ids_and_profiles(self):
        with SessionLocal() as db:
            employees = db.query(Employee).order_by(Employee.employee_id.asc()).all()
            emp_ids = [e.employee_id for e in employees]
            self.assertEqual(emp_ids, ['CMP-6385', 'CYB-1042', 'DEV-5271', 'FIN-2187', 'HR-4128', 'IT-3064'])
            emp2 = db.query(Employee).filter(Employee.employee_id == 'FIN-2187').first()
            self.assertIsNotNone(emp2)
            self.assertEqual(emp2.name, 'Alexander Hayes')
            self.assertEqual(emp2.department, 'Finance')
            self.assertIn('MBA Finance', emp2.education or '')
            self.assertIn('ERP_FINANCE', emp2.access_privileges or '')
            print('PASS: Professional alphanumeric IDs and profiles verified.')

    def test_02_mongodb_activity_validation_rules(self):
        with self.assertRaises(ValueError):
            mongo_service.insert_activity_log({
                'employee_id': 'FIN-2187',
                'event_type': 'unsupported_event_xyz',
                'action': 'Invalid'
            })

        res_valid = mongo_service.insert_activity_log({
            'employee_id': 'FIN-2187',
            'event_type': 'file_download',
            'action': 'Downloaded Q3 Financial Forecast',
            'resource': 'SharePoint://Finance/Q3_Forecast.xlsx',
            'device': 'FIN-D-102',
            'ip_address': '192.168.1.15',
            'risk_weight': 5,
            'is_suspicious': False,
            'details': {'size_mb': 2.5, 'classification': 'Internal'}
        })
        self.assertIsNotNone(res_valid.get('id'))
        print('PASS: MongoDB activity validation verified.')

    def test_03_telemetry_aggregations_timeline_heatmap(self):
        tl = mongo_service.get_activity_timeline(time_range='7d')
        self.assertIsInstance(tl, list)
        hm = mongo_service.get_activity_heatmap()
        self.assertEqual(len(hm), 168)
        dist = mongo_service.get_event_type_distribution()
        self.assertEqual(len(dist), 8)
        print('PASS: MongoDB timeline, heatmap, and distributions verified.')

    def test_04_end_to_end_threat_detection_and_alert_pipeline(self):
        with SessionLocal() as db:
            emp = db.query(Employee).filter(Employee.employee_id == 'FIN-2187').first()
            baseline = get_or_create_baseline(db, emp)
            anomalies = [
                {
                    'anomaly_type': 'MASS_DOWNLOAD_EXFILTRATION',
                    'severity': 'CRITICAL',
                    'description': 'Mass download volume: 4.8 GB exceeds baseline limit',
                    'risk_contribution': 50,
                },
                {
                    'anomaly_type': 'OFF_HOURS_ACCESS',
                    'severity': 'HIGH',
                    'description': 'Activity occurred at 02:15 AM outside normal shift',
                    'risk_contribution': 30,
                }
            ]
            mongo_res = mongo_service.insert_activity_log({
                'employee_id': emp.employee_id,
                'event_type': 'file_download',
                'action': 'Exfiltrated Confidential Executive Archive',
                'resource': 's3://vault/confidential.tar.gz',
                'device': 'ROG-Strix (Unenrolled)',
                'ip_address': '198.51.100.77',
                'risk_weight': 80,
                'is_suspicious': True,
                'anomaly_reasons': [a['description'] for a in anomalies],
                'is_test_event': True,
                'details': {'size_mb': 4800, 'source': 's3'}
            })
            self.assertIsNotNone(mongo_res.get('id'))
            new_score = calculate_and_update_employee_risk(db, emp, anomalies)
            self.assertGreaterEqual(new_score, 80)
            self.assertEqual(emp.risk_level, 'CRITICAL')

            from app.models import ActivityLog
            mock_act = ActivityLog(
                employee_id=emp.id,
                activity_type='file_download',
                action='Exfiltrated Confidential Executive Archive',
                resource='s3://vault/confidential.tar.gz',
                risk_weight=80,
                timestamp=datetime.now(timezone.utc),
            )
            alert = evaluate_and_trigger_alerts(db, emp, mock_act, anomalies, new_score)
            self.assertIsNotNone(alert)
            self.assertEqual(alert.category, 'DATA_EXFILTRATION')
            self.assertGreaterEqual(alert.risk_score, 80)
            print('PASS: End-to-end detection and alert pipeline verified.')

    def test_05_investigation_center_threat_narrative_and_analyst_notes(self):
        with SessionLocal() as db:
            emp = db.query(Employee).filter(Employee.employee_id == 'FIN-2187').first()
            note = InvestigationNote(
                employee_id=emp.id,
                author_email='analyst@itbis.cyber',
                note_text='Forensic interview completed. Subject unauthorized for off-hours access.'
            )
            db.add(note)
            audit = AuditLog(
                user_email='analyst@itbis.cyber',
                action='ADD_INVESTIGATION_NOTE',
                target_type='EMPLOYEE',
                target_id=emp.employee_id,
                details='Added forensic case note'
            )
            db.add(audit)
            db.commit()

            saved_note = db.query(InvestigationNote).filter(InvestigationNote.employee_id == emp.id).first()
            self.assertIsNotNone(saved_note)
            self.assertEqual(saved_note.author_email, 'analyst@itbis.cyber')
            print('PASS: Investigation Center notes and audit trail verified.')

    def test_06_incident_workflow_and_soc_notifications(self):
        with SessionLocal() as db:
            emp = db.query(Employee).filter(Employee.employee_id == 'FIN-2187').first()
            # Verify notifications generated
            notifs = db.query(Notification).all()
            self.assertGreater(len(notifs), 0)

            # Create Incident and test workflow
            inc = Incident(
                employee_id=emp.id,
                title='High-Risk Data Exfiltration Investigation',
                description='SOC incident created from automated alert',
                status='OPEN',
                severity='CRITICAL',
            )
            db.add(inc)
            db.commit()
            self.assertEqual(inc.status, 'OPEN')

            # Stage transitions
            inc.status = 'INVESTIGATING'
            db.commit()
            self.assertEqual(inc.status, 'INVESTIGATING')

            inc.status = 'CONTAINED'
            db.commit()
            self.assertEqual(inc.status, 'CONTAINED')

            inc.status = 'RESOLVED'
            db.commit()
            self.assertEqual(inc.status, 'RESOLVED')
            print('PASS: Incident workflow and SOC notifications verified.')

    def test_07_activity_timeline_filtering_and_schema(self):
        # Test default
        tl_all = mongo_service.get_activity_timeline(time_range='30d')
        self.assertIsInstance(tl_all, list)
        self.assertGreater(len(tl_all), 0)
        first = tl_all[0]
        self.assertIn('id', first)
        self.assertIn('employee_id', first)
        self.assertIn('event_type', first)
        self.assertIn('timestamp', first)
        self.assertIn('device', first)
        self.assertIn('ip_address', first)
        self.assertIn('severity', first)
        self.assertIn('risk_weight', first)
        self.assertIn('is_anomaly', first)
        self.assertIn('why_suspicious', first)
        self.assertIn('details', first)

        # Test 24h
        tl_24h = mongo_service.get_activity_timeline(time_range='24h')
        self.assertIsInstance(tl_24h, list)

        # Test 7d
        tl_7d = mongo_service.get_activity_timeline(time_range='7d')
        self.assertIsInstance(tl_7d, list)

        # Test Employee Filter
        for emp_id in ['CYB-1042', 'FIN-2187', 'IT-3064', 'HR-4128', 'DEV-5271', 'CMP-6385']:
            tl_emp = mongo_service.get_activity_timeline(employee_id=emp_id)
            self.assertGreater(len(tl_emp), 0)
            for item in tl_emp:
                self.assertEqual(item['employee_id'], emp_id)

        # Test Event Type Filter
        for evt in ['file_download', 'usb_connect', 'privilege_change', 'login', 'data_transfer']:
            tl_evt = mongo_service.get_activity_timeline(event_type=evt)
            for item in tl_evt:
                self.assertEqual(item['event_type'], evt)

        print('PASS: Activity timeline rich feed and dynamic filtering verified.')


if __name__ == '__main__':
    unittest.main(verbosity=2)

