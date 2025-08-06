from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import date
import re

class EMRRecord(BaseModel):
    patient_id: str
    name: str
    dob: date
    gender: str
    email: EmailStr
    diagnosis_code: str
    heart_rate: int
    blood_pressure_systolic: int
    blood_pressure_diastolic: int

    @validator('gender')
    def validate_gender(cls, v):
        if v not in ["Male", "Female", "Other"]:
            raise ValueError("Invalid gender")
        return v

    @validator('diagnosis_code')
    def validate_icd10(cls, v):
        if not re.match(r"^[A-Z]\d{2}$", v):
            raise ValueError("Invalid ICD-10 code format")
        return v

    @validator('heart_rate')
    def validate_heart_rate(cls, v):
        if not 30 <= v <= 200:
            raise ValueError("Heart rate out of range")
        return v
