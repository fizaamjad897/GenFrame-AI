"""
Organisation Module JWT Validation

This module handles JWT tokens issued by the NestJS Organisation Module.
It validates tokens and auto-creates Visual Engine user records on first access.
"""

import os
import jwt
from datetime import datetime
from typing import Optional
from fastapi import HTTPException
from jose import JWTError
import auth as auth_module


# Organisation Module JWT Secret (must match NestJS env)
ORGANISATION_JWT_SECRET = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ORGANISATION_JWT_SECRET = ORGANISATION_JWT_SECRET.strip("'\" ")


def validate_org_module_jwt(token: str) -> dict:
    """
    Validate JWT from Organisation Module and return user data.
    
    This function:
    1. Decodes the JWT using the shared JWT_SECRET
    2. Extracts user and organisation information
    3. Looks up the user in Visual Engine DB by org_module_user_id
    4. Auto-creates a Visual Engine user record on first access
    5. Returns the Visual Engine user document
    
    Args:
        token: JWT token from Authorization: Bearer <token> header
        
    Returns:
        dict: Visual Engine user document
        
    Raises:
        HTTPException: If token is invalid, expired, or user creation fails
    """
    try:
        # Decode using shared secret
        payload = jwt.decode(
            token,
            ORGANISATION_JWT_SECRET,
            algorithms=["HS256"]
        )
        
        # Extract essential fields from Organisation Module JWT
        # Be tolerant to claim-name variations across environments.
        org_user_id = payload.get("userId") or payload.get("user_id") or payload.get("id")
        org_id = payload.get("orgId") or payload.get("org_id") or payload.get("organizationId")
        user_email = payload.get("userEmail") or payload.get("email")
        user_name = payload.get("userName") or payload.get("name")
        user_role = payload.get("userRole") or payload.get("role") or "user"
        org_customer_type_raw = payload.get("orgCustomerType")
        org_transform_price_raw = payload.get("orgTransformationCreditPrice")
        org_creation_price_raw = payload.get("orgCreationCreditPrice")
        org_transform_threshold_raw = payload.get("orgTransformationCreditsThreshold")
        org_creation_threshold_raw = payload.get("orgCreationCreditsThreshold")
        org_customer_type = str(org_customer_type_raw) if org_customer_type_raw is not None else None
        is_postpaid: Optional[bool] = None
        if org_customer_type is not None:
            is_postpaid = org_customer_type.lower() == "postpaid"
        else:
            # Backward-compatible fallback for tokens that don't include orgCustomerType.
            org_type_name = str(payload.get("orgTypeName") or payload.get("orgType") or "")
            if org_type_name.lower() == "suborg":
                is_postpaid = True

        org_transform_price: Optional[float] = None
        org_creation_price: Optional[float] = None
        org_transform_threshold: Optional[float] = None
        org_creation_threshold: Optional[float] = None
        try:
            if org_transform_price_raw is not None:
                org_transform_price = float(org_transform_price_raw)
        except (TypeError, ValueError):
            org_transform_price = None
        try:
            if org_creation_price_raw is not None:
                org_creation_price = float(org_creation_price_raw)
        except (TypeError, ValueError):
            org_creation_price = None
        try:
            if org_transform_threshold_raw is not None:
                org_transform_threshold = float(org_transform_threshold_raw)
        except (TypeError, ValueError):
            org_transform_threshold = None
        try:
            if org_creation_threshold_raw is not None:
                org_creation_threshold = float(org_creation_threshold_raw)
        except (TypeError, ValueError):
            org_creation_threshold = None
        
        # Validate required fields
        if not org_user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing userId"
            )
        if not org_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing orgId"
            )
        if not user_email:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing userEmail"
            )
        
        # Look up Visual Engine user by org_module_user_id (set during migration)
        visual_engine_user = auth_module.users_collection.find_one(
            {"org_module_user_id": org_user_id}
        )

        # Keep pay model and org credit rates aligned with Organisation Module on each login.
        if visual_engine_user:
            update_set = {"updatedAt": datetime.utcnow()}
            should_update = False

            if (
                is_postpaid is not None
                and bool(visual_engine_user.get("is_postpaid", False)) != is_postpaid
            ):
                update_set["is_postpaid"] = is_postpaid
                visual_engine_user["is_postpaid"] = is_postpaid
                should_update = True

            engine_data = visual_engine_user.get("engine_data", {}) or {}
            transformation_engine = engine_data.get("transformation", {}) or {}
            creation_engine = engine_data.get("creation", {}) or {}
            transformation_credits = transformation_engine.get("credits", {}) or {}
            creation_credits = creation_engine.get("credits", {}) or {}

            if org_transform_price is not None and float(transformation_credits.get("overageRate", 0.19)) != org_transform_price:
                update_set["engine_data.transformation.credits.overageRate"] = org_transform_price
                if visual_engine_user.get("engineType") == "transformation":
                    update_set["credits.overageRate"] = org_transform_price
                    visual_engine_user.setdefault("credits", {})["overageRate"] = org_transform_price
                transformation_credits["overageRate"] = org_transform_price
                should_update = True

            if org_creation_price is not None and float(creation_credits.get("overageRate", 0.19)) != org_creation_price:
                update_set["engine_data.creation.credits.overageRate"] = org_creation_price
                if visual_engine_user.get("engineType") == "creation":
                    update_set["credits.overageRate"] = org_creation_price
                    visual_engine_user.setdefault("credits", {})["overageRate"] = org_creation_price
                creation_credits["overageRate"] = org_creation_price
                should_update = True

            # Sync thresholds from org module
            current_transform_threshold = float(visual_engine_user.get("transformation_threshold", 0))
            current_creation_threshold = float(visual_engine_user.get("creation_threshold", 0))
            if org_transform_threshold is not None and current_transform_threshold != org_transform_threshold:
                update_set["transformation_threshold"] = org_transform_threshold
                should_update = True
            if org_creation_threshold is not None and current_creation_threshold != org_creation_threshold:
                update_set["creation_threshold"] = org_creation_threshold
                should_update = True

            if should_update:
                auth_module.users_collection.update_one(
                    {"_id": visual_engine_user["_id"]},
                    {"$set": update_set},
                )
        
        # If user doesn't exist in Visual Engine, auto-create
        if not visual_engine_user:
            print(f"[ORG_AUTH] Auto-creating Visual Engine user for org_user_id: {org_user_id}")
            visual_engine_user = _create_visual_engine_user_for_org_user(
                org_user_id=org_user_id,
                org_id=org_id,
                email=user_email,
                name=user_name,
                is_postpaid=is_postpaid,
                transformation_credit_price=org_transform_price,
                creation_credit_price=org_creation_price,
            )
        
        # Extract parent org ID (for sub-org access control)
        parent_org_id = (
            payload.get("parentOrgId")
            or payload.get("orgParentId")
            or payload.get("parent_org_id")
        )
        
        # If parentOrgId not in JWT, query the org document to get it
        if not parent_org_id and auth_module.org_organisations_collection is not None:
            try:
                org_doc = auth_module.org_organisations_collection.find_one({"id": org_id})
                if org_doc:
                    parent_org_id = org_doc.get("parentOrgId")
            except Exception as e:
                print(f"[ORG_AUTH] Failed to query org document for parentOrgId: {e}")
        
        # Enrich user object with org context from JWT payload
        visual_engine_user["_org_context"] = {
            "org_id": org_id,
            "parent_org_id": parent_org_id,
            "role": user_role,
            "org_name": payload.get("orgName"),
            "org_type": payload.get("orgTypeName"),
            "selected_engines": payload.get("orgSelectedEngines") or [],
            "customer_type": org_customer_type,
            "transformation_credit_price": org_transform_price,
            "creation_credit_price": org_creation_price,
            "transformation_threshold": org_transform_threshold,
            "creation_threshold": org_creation_threshold,
        }
        
        return visual_engine_user
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ORG_AUTH] Unexpected error validating org JWT: {e}")
        raise HTTPException(
            status_code=500,
            detail="Authentication service error"
        )


def _create_visual_engine_user_for_org_user(
    org_user_id: str,
    org_id: str,
    email: str,
    name: str = None,
    is_postpaid: Optional[bool] = None,
    transformation_credit_price: Optional[float] = None,
    creation_credit_price: Optional[float] = None,
) -> dict:
    """
    Auto-create a Visual Engine user record for a new Organisation Module user.
    
    This is called on first JWT access when the user doesn't exist in Visual Engine.
    The user is created with zero credits and empty plan.
    
    Args:
        org_user_id: UUID from Organisation Module
        org_id: Organisation ID from Organisation Module
        email: User's email from Organisation Module
        name: User's name from Organisation Module (optional)
        
    Returns:
        dict: The newly created user document
    """
    try:
        now = datetime.utcnow()
        email_normalized = (email or "").strip().lower()
        transformation_rate = float(transformation_credit_price) if transformation_credit_price is not None else 0.19
        creation_rate = float(creation_credit_price) if creation_credit_price is not None else 0.19
        
        user_doc = {
            # CRITICAL: Link to Organisation Module user
            "org_module_user_id": org_user_id,
            "organisation_id": org_id,
            # Safe fallback: if customer type is missing, keep user as prepaid.
            "is_postpaid": bool(is_postpaid) if is_postpaid is not None else False,
            
            # User info from Org Module
            "email": email_normalized,
            "fullName": name or "",
            
            # Plan and credits (empty on creation)
            "plan": "",
            "engineType": "transformation",
            "units": 0,
            "maxUnits": 200,
            
            # Comprehensive credits structure
            "credits": {
                "monthly_units_used": 0.0,
                "monthly_units_max": 0.0,
                "addon_units_used": 0.0,
                "addon_units_max": 0.0,
                "remaining_units": 0.0,
                "overageRate": transformation_rate,
            },
            
            # Engine-specific data (isolated per engine type)
            "engine_data": {
                "transformation": {
                    "plan": "",
                    "credits": {
                        "monthly_units_used": 0.0,
                        "monthly_units_max": 0.0,
                        "addon_units_used": 0.0,
                        "addon_units_max": 0.0,
                        "remaining_units": 0.0,
                        "overageRate": transformation_rate,
                    },
                    "is_pending_cancellation": False,
                    "stripeSubscriptionId": None,
                    "updatedAt": now
                },
                "creation": {
                    "plan": "",
                    "credits": {
                        "monthly_units_used": 0.0,
                        "monthly_units_max": 0.0,
                        "addon_units_used": 0.0,
                        "addon_units_max": 0.0,
                        "remaining_units": 0.0,
                        "overageRate": creation_rate,
                    },
                    "is_pending_cancellation": False,
                    "stripeSubscriptionId": None,
                    "updatedAt": now
                }
            },
            
            # API keys (populated later)
            "api_keys": {
                "resize_hash": None,
                "create_hash": None
            },
            
            # Stripe (populated when user creates subscription)
            "stripeCustomerId": None,
            "stripeSubscriptionId": None,
            
            # Timestamps
            "createdAt": now,
            "updatedAt": now,
        }
        
        # Insert into Visual Engine DB
        try:
            result = auth_module.users_collection.insert_one(user_doc)
            user_doc["_id"] = result.inserted_id
            
            print(f"[ORG_AUTH] Created Visual Engine user {result.inserted_id} for org_user {org_user_id}")
            return user_doc
        
        except Exception as insert_error:
            # Handle duplicate key error (email already exists)
            # This happens when user created VE account first, then migrated to Org Module
            if "E11000" in str(insert_error) and "email" in str(insert_error):
                print(f"[ORG_AUTH] Email {email_normalized} already exists, attempting to link org_module_user_id")
                
                # Find and update existing user with org linking
                existing_user = auth_module.users_collection.find_one({"email": email_normalized})
                if not existing_user and email_normalized:
                    # Extra safety for legacy records that may have different casing/spacing.
                    existing_user = auth_module.users_collection.find_one(
                        {"email": {"$regex": f"^{email_normalized}$", "$options": "i"}}
                    )
                if existing_user:
                    # Update with org linking fields
                    auth_module.users_collection.update_one(
                        {"_id": existing_user["_id"]},
                        {
                            "$set": {
                                "org_module_user_id": org_user_id,
                                "organisation_id": org_id,
                                "fullName": name or existing_user.get("fullName", ""),
                                "updatedAt": now
                            }
                        }
                    )
                    print(f"[ORG_AUTH] Linked existing user {existing_user['_id']} to org_user {org_user_id}")
                    
                    # Return updated user
                    existing_user["org_module_user_id"] = org_user_id
                    existing_user["organisation_id"] = org_id
                    if name:
                        existing_user["fullName"] = name
                    return existing_user
                else:
                    print(f"[ORG_AUTH] Email duplicate but user not found: {email}")
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to provision user account: duplicate email but user not found"
                    )
            else:
                print(f"[ORG_AUTH] Failed to create Visual Engine user: {insert_error}")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to provision user account"
                )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ORG_AUTH] Unexpected error during user creation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to provision user account"
        )


def get_org_context_from_user(user: dict) -> dict:
    """
    Extract organisation context from a Visual Engine user document.
    
    This context is attached by validate_org_module_jwt() and contains
    information from the original Organisation Module JWT.
    
    Args:
        user: Visual Engine user document
        
    Returns:
        dict: Organisation context (org_id, role, org_name, org_type)
              Empty dict if no org context (legacy JWT auth)
    """
    return user.get("_org_context", {})
