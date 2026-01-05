from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PlanSchema(BaseModel):
    """Schema for pricing plans"""
    name: str  # "Starter", "Growth", "Scale"
    price: float  # Monthly price in USD
    includedUnits: int  # Number of units included
    costPerUnit: float  # Cost per unit
    bestFor: str  # Description of who it's best for
    features: List[str]  # List of features
    isActive: bool = True
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

class UsageLogSchema(BaseModel):
    """Schema for tracking individual usage operations"""
    userId: str
    operation: str  # "resize", "generate", etc.
    aspectRatio: str
    timestamp: datetime
    success: bool
    imageUrl: Optional[str] = None

class BillingRecordSchema(BaseModel):
    """Schema for monthly billing records"""
    userId: str
    billingPeriodStart: datetime
    billingPeriodEnd: datetime
    plan: str
    basePrice: float
    includedUnits: int
    unitsUsed: int
    overageUnits: int
    overageCharge: float  # overageUnits * 0.19
    totalAmount: float  # basePrice + overageCharge
    generatedAt: datetime
    status: str  # "pending", "paid", "overdue"
