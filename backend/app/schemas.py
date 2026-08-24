from typing import Optional

from pydantic import BaseModel


class EmployeeCreate(BaseModel):

    employee_id: str

    name: str

    department: Optional[str] = None

    designation: Optional[str] = None

    manager_id: Optional[str] = None

    device_info: Optional[str] = None

    access_privileges: Optional[str] = None


class ActivityCreate(BaseModel):

    employee_id: str

    activity_type: str

    resource: Optional[str] = None

    timestamp: Optional[str] = None

    ip_address: Optional[str] = None

    device: Optional[str] = None