from fastapi import APIRouter, Depends, HTTPException, Body, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random
from .auth import get_current_user

# Create router for Monitoring
router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])

# Models for monitoring data
class SensorReading(BaseModel):
    timestamp: datetime
    value: float
    unit: str
    status: str  # Normal, Warning, Alert

class SensorData(BaseModel):
    sensor_id: str
    sensor_name: str
    sensor_type: str
    location: str
    readings: List[SensorReading]
    last_reading: SensorReading
    status: str  # Online, Offline, Maintenance

class MonitoringAlert(BaseModel):
    alert_id: str
    facility_id: str
    sensor_id: str
    timestamp: datetime
    alert_type: str
    severity: str  # Low, Medium, High, Critical
    message: str
    status: str  # Active, Acknowledged, Resolved
    acknowledged_by: Optional[str] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None

class MonitoringDashboardResponse(BaseModel):
    facility_id: str
    facility_name: str
    overall_status: str  # Normal, Warning, Alert
    sensors_count: Dict[str, int]  # Count by status
    alerts_count: Dict[str, int]  # Count by severity
    recent_alerts: List[MonitoringAlert]
    last_updated: datetime

# Sample sensor types and their units
sensor_types = {
    "piezometer": "kPa",
    "inclinometer": "mm",
    "water_level": "m",
    "flow_rate": "L/s",
    "rainfall": "mm",
    "temperature": "°C",
    "ph": "pH",
    "conductivity": "μS/cm",
    "turbidity": "NTU",
    "settlement": "mm"
}

# Sample facilities
sample_facilities = {
    "FAC001": {"name": "North Basin Facility", "status": "Normal"},
    "FAC002": {"name": "South Basin Facility", "status": "Warning"},
    "FAC003": {"name": "East Basin Facility", "status": "Normal"},
    "FAC004": {"name": "West Basin Facility", "status": "Alert"}
}

# Generate sample sensor data
def generate_sample_sensors(facility_id: str, count: int = 10):
    sensors = []
    locations = ["Dam Crest", "Upstream Slope", "Downstream Slope", "Foundation", "Spillway", "Decant Pond"]
    statuses = ["Online", "Online", "Online", "Online", "Maintenance", "Offline"]
    
    for i in range(count):
        sensor_type = random.choice(list(sensor_types.keys()))
        unit = sensor_types[sensor_type]
        status = random.choice(statuses)
        
        # Generate readings for the past 24 hours
        now = datetime.now()
        readings = []
        
        for hour in range(24, 0, -1):
            timestamp = now - timedelta(hours=hour)
            
            # Base value depends on sensor type
            if sensor_type == "piezometer":
                base_value = random.uniform(50, 150)
            elif sensor_type == "inclinometer":
                base_value = random.uniform(0, 5)
            elif sensor_type == "water_level":
                base_value = random.uniform(10, 20)
            elif sensor_type == "flow_rate":
                base_value = random.uniform(5, 15)
            elif sensor_type == "rainfall":
                base_value = random.uniform(0, 10)
            elif sensor_type == "temperature":
                base_value = random.uniform(15, 25)
            elif sensor_type == "ph":
                base_value = random.uniform(6.5, 8.5)
            elif sensor_type == "conductivity":
                base_value = random.uniform(200, 800)
            elif sensor_type == "turbidity":
                base_value = random.uniform(0, 20)
            elif sensor_type == "settlement":
                base_value = random.uniform(0, 10)
            else:
                base_value = random.uniform(0, 100)
            
            # Add some random variation
            value = base_value + random.uniform(-2, 2)
            
            # Determine status based on value
            if sensor_type == "piezometer" and value > 140:
                reading_status = "Alert"
            elif sensor_type == "inclinometer" and value > 4:
                reading_status = "Warning"
            elif sensor_type == "water_level" and value > 18:
                reading_status = "Warning"
            elif sensor_type == "ph" and (value < 6.8 or value > 8.2):
                reading_status = "Warning"
            else:
                reading_status = "Normal"
            
            readings.append(SensorReading(
                timestamp=timestamp,
                value=round(value, 2),
                unit=unit,
                status=reading_status
            ))
        
        # Latest reading
        latest_value = readings[-1].value + random.uniform(-0.5, 0.5)
        
        if sensor_type == "piezometer" and latest_value > 140:
            latest_status = "Alert"
        elif sensor_type == "inclinometer" and latest_value > 4:
            latest_status = "Warning"
        elif sensor_type == "water_level" and latest_value > 18:
            latest_status = "Warning"
        elif sensor_type == "ph" and (latest_value < 6.8 or latest_value > 8.2):
            latest_status = "Warning"
        else:
            latest_status = "Normal"
        
        latest_reading = SensorReading(
            timestamp=now,
            value=round(latest_value, 2),
            unit=unit,
            status=latest_status
        )
        
        sensors.append(SensorData(
            sensor_id=f"SEN{facility_id[-3:]}{i+1:03d}",
            sensor_name=f"{sensor_type.capitalize()} {i+1}",
            sensor_type=sensor_type,
            location=random.choice(locations),
            readings=readings,
            last_reading=latest_reading,
            status=status
        ))
    
    return sensors

# Generate sample alerts
def generate_sample_alerts(facility_id: str, count: int = 5):
    alerts = []
    alert_types = ["High Reading", "Sensor Offline", "Rapid Change", "Threshold Exceeded", "Communication Error"]
    severities = ["Low", "Medium", "High", "Critical"]
    statuses = ["Active", "Acknowledged", "Resolved"]
    
    for i in range(count):
        alert_type = random.choice(alert_types)
        severity = random.choice(severities)
        status = random.choice(statuses)
        
        # Generate timestamp within the past week
        hours_ago = random.randint(1, 168)  # Up to 1 week ago
        timestamp = datetime.now() - timedelta(hours=hours_ago)
        
        # Generate message based on alert type
        if alert_type == "High Reading":
            message = "Sensor reading exceeds threshold value"
        elif alert_type == "Sensor Offline":
            message = "Sensor has gone offline and is not reporting data"
        elif alert_type == "Rapid Change":
            message = "Rapid change in sensor readings detected"
        elif alert_type == "Threshold Exceeded":
            message = "Monitoring threshold has been exceeded"
        elif alert_type == "Communication Error":
            message = "Communication error with sensor detected"
        
        # Add user info for acknowledged/resolved alerts
        acknowledged_by = None
        resolved_by = None
        resolution_notes = None
        
        if status == "Acknowledged" or status == "Resolved":
            acknowledged_by = "John Smith"
            
            if status == "Resolved":
                resolved_by = "John Smith"
                resolution_notes = "Issue investigated and resolved. No further action required."
        
        alerts.append(MonitoringAlert(
            alert_id=f"ALT{facility_id[-3:]}{i+1:03d}",
            facility_id=facility_id,
            sensor_id=f"SEN{facility_id[-3:]}{random.randint(1, 10):03d}",
            timestamp=timestamp,
            alert_type=alert_type,
            severity=severity,
            message=message,
            status=status,
            acknowledged_by=acknowledged_by,
            resolved_by=resolved_by,
            resolution_notes=resolution_notes
        ))
    
    # Sort by timestamp, most recent first
    alerts.sort(key=lambda x: x.timestamp, reverse=True)
    
    return alerts

@router.get("/facilities", response_model=List[Dict[str, Any]])
async def get_facilities(current_user: dict = Depends(get_current_user)):
    """Get list of facilities with monitoring status summary"""
    facilities_list = []
    for facility_id, facility_data in sample_facilities.items():
        facilities_list.append({
            "id": facility_id,
            "name": facility_data["name"],
            "status": facility_data["status"]
        })
    return facilities_list

@router.get("/dashboard/{facility_id}", response_model=MonitoringDashboardResponse)
async def get_monitoring_dashboard(
    facility_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get monitoring dashboard data for a specific facility"""
    if facility_id not in sample_facilities:
        raise HTTPException(status_code=404, detail="Facility not found")
    
    facility = sample_facilities[facility_id]
    
    # Generate sample sensors and alerts
    sensors = generate_sample_sensors(facility_id)
    alerts = generate_sample_alerts(facility_id)
    
    # Count sensors by status
    sensors_count = {
        "Online": sum(1 for s in sensors if s.status == "Online"),
        "Offline": sum(1 for s in sensors if s.status == "Offline"),
        "Maintenance": sum(1 for s in sensors if s.status == "Maintenance"),
        "Total": len(sensors)
    }
    
    # Count alerts by severity
    alerts_count = {
        "Critical": sum(1 for a in alerts if a.severity == "Critical"),
        "High": sum(1 for a in alerts if a.severity == "High"),
        "Medium": sum(1 for a in alerts if a.severity == "Medium"),
        "Low": sum(1 for a in alerts if a.severity == "Low"),
        "Total": len(alerts)
    }
    
    return {
        "facility_id": facility_id,
        "facility_name": facility["name"],
        "overall_status": facility["status"],
        "sensors_count": sensors_count,
        "alerts_count": alerts_count,
        "recent_alerts": alerts[:5],  # Only return 5 most recent alerts
        "last_updated": datetime.now()
    }

@router.get("/sensors/{facility_id}", response_model=List[SensorData])
async def get_facility_sensors(
    facility_id: str,
    sensor_type: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Get sensors for a specific facility with optional filtering"""
    if facility_id not in sample_facilities:
        raise HTTPException(status_code=404, detail="Facility not found")
    
    # Generate sample sensors
    sensors = generate_sample_sensors(facility_id)
    
    # Apply filters if provided
    if sensor_type:
        sensors = [s for s in sensors if s.sensor_type == sensor_type]
    
    if location:
        sensors = [s for s in sensors if s.location == location]
    
    if status:
        sensors = [s for s in sensors if s.status == status]
    
    return sensors

@router.get("/sensor/{sensor_id}", response_model=SensorData)
async def get_sensor_data(
    sensor_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed data for a specific sensor"""
    # Extract facility ID from sensor ID
    facility_id = f"FAC{sensor_id[3:6]}"
    
    if facility_id not in sample_facilities:
        raise HTTPException(status_code=404, detail="Facility not found")
    
    # Generate sample sensors
    sensors = generate_sample_sensors(facility_id)
    
    # Find the requested sensor
    for sensor in sensors:
        if sensor.sensor_id == sensor_id:
            return sensor
    
    raise HTTPException(status_code=404, detail="Sensor not found")

@router.get("/alerts/{facility_id}", response_model=List[MonitoringAlert])
async def get_facility_alerts(
    facility_id: str,
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Get alerts for a specific facility with optional filtering"""
    if facility_id not in sample_facilities:
        raise HTTPException(status_code=404, detail="Facility not found")
    
    # Generate sample alerts
    alerts = generate_sample_alerts(facility_id, 20)  # Generate more alerts for filtering
    
    # Apply filters if provided
    if severity:
        alerts = [a for a in alerts if a.severity == severity]
    
    if status:
        alerts = [a for a in alerts if a.status == status]
    
    return alerts

@router.post("/alerts/{alert_id}/acknowledge", response_model=MonitoringAlert)
async def acknowledge_alert(
    alert_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Acknowledge an alert"""
    # Extract facility ID from alert ID
    facility_id = f"FAC{alert_id[3:6]}"
    
    if facility_id not in sample_facilities:
        raise HTTPException(status_code=404, detail="Facility not found")
    
    # Generate sample alerts
    alerts = generate_sample_alerts(facility_id)
    
    # Find the requested alert
    for alert in alerts:
        if alert.alert_id == alert_id:
            if alert.status != "Active":
                raise HTTPException(status_code=400, detail="Alert is not active")
            
            # Update alert status
            alert.status = "Acknowledged"
            alert.acknowledged_by = f"{current_user['username']}"
            
            return alert
    
    raise HTTPException(status_code=404, detail="Alert not found")

@router.post("/alerts/{alert_id}/resolve", response_model=MonitoringAlert)
async def resolve_alert(
    alert_id: str,
    notes: str = Body(..., embed=True),
    current_user: dict = Depends(get_current_user)
):
    """Resolve an alert with resolution notes"""
    # Extract facility ID from alert ID
    facility_id = f"FAC{alert_id[3:6]}"
    
    if facility_id not in sample_facilities:
        raise HTTPException(status_code=404, detail="Facility not found")
    
    # Generate sample alerts
    alerts = generate_sample_alerts(facility_id)
    
    # Find the requested alert
    for alert in alerts:
        if alert.alert_id == alert_id:
            if alert.status == "Resolved":
                raise HTTPException(status_code=400, detail="Alert is already resolved")
            
            # Update alert status
            alert.status = "Resolved"
            alert.resolved_by = f"{current_user['username']}"
            alert.resolution_notes = notes
            
            return alert
    
    raise HTTPException(status_code=404, detail="Alert not found")
