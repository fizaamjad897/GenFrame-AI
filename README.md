# Visual Engine: AI-Powered Image Processing Backend

Visual Engine is a high-performance FastAPI backend that leverages Gemini's vision models for intelligent image transformation and creative generation. It features a specialized **Pixel-Aware Token System** and seamless **Stripe Integration** for subscription management.

---

## 🚀 Quick Start (Local Setup)

### 1. Prerequisites
- Python 3.9+
- MongoDB (Local or Atlas)
- Google Gemini API Key
- Stripe Account (for payment testing)

### 2. Installation
```powershell
# Clone the repository and navigate to the folder
cd Visual-Engine-BE

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```env
# Core API Keys
GOOGLE_API_KEY=your_gemini_key
MONGODB_URL=your_mongodb_connection_string
DB_NAME=visual_engine_secure
JWT_SECRET=your_jwt_secret

# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_M_STARTER=price_...
# (Include all M_ and T_ price IDs)

# Storage (Digital Ocean)
DO_ACCESS_KEY_ID=...
DO_SECRET_KEY=...
ENDPOINT=...
SPACENAME=...
```

---

## 🛠️ Local Testing Guide (Postman/CURL)

### 1. Start the Server
```powershell
uvicorn main:app --reload
```
Server runs at: `http://127.0.0.1:8000`

### 2. Base Authentication
| Task | Method | Endpoint | Body (JSON) |
| :--- | :--- | :--- | :--- |
| **Register** | POST | `/api/users/register` | `{"email": "...", "password": "..."}` |
| **Login** | POST | `/api/users/login` | `{"email": "...", "password": "..."}` |
| **Get Usage** | GET | `/api/users/usage` | Requires JWT Bearer Token |

### 3. Engine Processing (API Key Auth)
For these tests, use the header: `X-API-KEY: <YOUR_KEY>`

```bash
# Example: Transformation Engine (Resize)
curl -X POST "http://127.0.0.1:8000/api/resize" \
     -H "X-API-KEY: YOUR_RESIZE_KEY" \
     -F "file=@image.jpg" \
     -F "aspect_ratio=16:9"
```

---

## 🤝 Client Handover (Glenn FMCTV)

### 1. Access Credentials
| Credential | Value |
| :--- | :--- |
| **Email** | `glenn@fmctv.co.nz` |
| **Password** | `VisualEngine2026!` |
| **Test Balance** | 50.0 Tokens |

### 2. Active Engine Keys
| Engine | Required Header | Key Value |
| :--- | :--- | :--- |
| **Transformation** | `X-API-KEY` | `PX-dFN_Ap7Z8PNnbSY6HIuHltuNtt6NGM1lExaBK-b4` |
| **Creation** | `X-API-KEY` | `SQG9Wr3gebI2Os_mXWBEDrjsPCEkxr3AKInMxqdSPJI` |

### 3. Token Billing Rules
The system automatically selects the billing tier based on image resolution.

| Operation Tier | Transformation | Creation |
| :--- | :--- | :--- |
| **Standard** (≤ 1024px) | 1.0 Units | 2.5 Units |
| **Premium** (> 1024px) | 2.5 Units | 4.5 Units |

**Detection Header**: Every response contains `X-Is-Large-Image: true/false`.

---

## 📖 API Documentation Summary

| Endpoint | Method | Auth | Description |
| :--- | :--- | :--- | :--- |
| `/api/resize` | POST | API Key | Structural image resizing. |
| `/api/create` | POST | API Key | AI-powered creative generation. |
| `/api/users/usage` | GET | JWT | Live token balance monitoring. |
| `/api/users/engine-type` | POST | JWT | Switch between Transformation/Creation mode. |
| `/api/stripe/create-checkout`| POST | JWT | Initialize subscription payment. |
| `/api/users/api-key` | POST | JWT | Generate new scoped API keys. |

---

## 🛡️ Security Features
- **Stateless API Keys**: Independent of user sessions for faster processing.
- **HMAC Hashing**: API keys are hashed in the database; original keys are never stored.
- **Rate Limiting**: Built-in protection against brute-force and DDoS attempts in `middleware.py`.
- **Pixel-Aware Logic**: Server-side resolution validation prevents token manipulation.
