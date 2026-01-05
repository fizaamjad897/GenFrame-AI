from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    fullName: Optional[str] = None
    fingerprint: Optional[str] = None
    presentationId: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    newPassword: str

class User(BaseModel):
    id: Optional[str] = None
    email: str
    fullName: Optional[str] = None
    plan: str = ""  # Default is no plan
    units: int = 0
    maxUnits: int = 200  # Default for free allotment
    createdAt: datetime = None
    updatedAt: datetime = None

class UserResponse(BaseModel):
    id: str
    email: str
    fullName: Optional[str] = None
    plan: str
    units: int
    maxUnits: int
    createdAt: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
class PlanUpgradeRequest(BaseModel):
    plan: str  # "starter", "growth", or "scale"

class Plan(BaseModel):
    """Pricing plan model"""
    id: Optional[str] = None
    name: str
    price: float
    includedUnits: int
    costPerUnit: float
    bestFor: str
    features: list[str]
    isActive: bool = True

class UsageLog(BaseModel):
    """Usage tracking model"""
    id: Optional[str] = None
    userId: str
    operation: str
    aspectRatio: str
    timestamp: datetime
    success: bool
    imageUrl: Optional[str] = None

class BillingRecord(BaseModel):
    """Billing record model"""
    id: Optional[str] = None
    userId: str
    billingPeriodStart: datetime
    billingPeriodEnd: datetime
    plan: str
    basePrice: float
    includedUnits: int
    unitsUsed: int
    overageUnits: int
    overageCharge: float
    totalAmount: float
    generatedAt: datetime
    status: str  # "pending", "paid", "overdue"