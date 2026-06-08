"use client";

import React, { useState } from "react";
import SignupForm from "./auth/SignupForm";
import LoginForm from "./auth/LoginForm";
import ForgotPasswordForm from "./auth/ForgotPasswordForm";
import ResetPasswordForm from "./auth/ResetPasswordForm";
import { toast } from "react-toastify";
import {
  forgotPassword,
  orgSignin,
  orgSignup,
  resetPassword,
} from "@/lib/organisationApi";
import { extractApiErrorMessage } from "@/lib/errorMessage";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import BoltIcon from "@mui/icons-material/Bolt";
import GridViewIcon from "@mui/icons-material/GridView";
import { useRouter } from "next/navigation";

interface AuthProps {
  onAuthSuccess?: (token: string, user: any) => void;
  initialTab?: ActiveForm;
  initialToken?: string;
  redirectTo?: string;
}

type FormData = {
  fullName: string;
  email: string;
  password: string;
  confirmPassword: string;
  agree: boolean;
  token?: string;
  newPassword?: string;
};

export type ActiveForm = "signup" | "login" | "forgot" | "reset";

const LogoIcon = ({ size = 36, gradId }: { size?: number; gradId: string }) => (
  <svg width={size} height={size} viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id={gradId} x1="0" y1="0" x2="36" y2="36" gradientUnits="userSpaceOnUse">
        <stop stopColor="#0C4A6E" /><stop offset="1" stopColor="#0EA5E9" />
      </linearGradient>
    </defs>
    <rect width="36" height="36" rx="10" fill={`url(#${gradId})`} />
    {/* Frame corners */}
    <path d="M9 9L9 14M9 9L14 9" stroke="white" strokeWidth="2.5" strokeLinecap="round" />
    <path d="M27 9L22 9M27 9L27 14" stroke="white" strokeWidth="2.5" strokeLinecap="round" />
    <path d="M9 27L9 22M9 27L14 27" stroke="white" strokeWidth="2.5" strokeLinecap="round" />
    <path d="M27 27L22 27M27 27L27 22" stroke="white" strokeWidth="2.5" strokeLinecap="round" />
    {/* AI sparkle */}
    <path d="M18 12L19.3 16.7L24 18L19.3 19.3L18 24L16.7 19.3L12 18L16.7 16.7Z" fill="white" />
  </svg>
);

const BRAND_FEATURES = [
  { icon: <AutoAwesomeIcon sx={{ fontSize: 16, color: "rgba(255,255,255,0.9)" }} />, text: "47+ platform format presets included" },
  { icon: <BoltIcon sx={{ fontSize: 16, color: "rgba(255,255,255,0.9)" }} />,        text: "AI adaptation in under 4 seconds" },
  { icon: <GridViewIcon sx={{ fontSize: 16, color: "rgba(255,255,255,0.9)" }} />,    text: "Full resolution export, no watermarks" },
  { icon: <CheckCircleIcon sx={{ fontSize: 16, color: "rgba(255,255,255,0.9)" }} />, text: "Works for Instagram, YouTube, LinkedIn & 44 more" },
];

const Auth: React.FC<AuthProps> = ({ onAuthSuccess, initialTab, initialToken, redirectTo }) => {
  const router = useRouter();
  const [formData, setFormData] = useState<FormData>({
    fullName: "",
    email: "",
    password: "",
    confirmPassword: "",
    agree: false,
    token: initialToken || "",
    newPassword: "",
  });
  const [activeForm, setActiveForm] = useState<ActiveForm>(initialTab || "login");
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const target = e.target as HTMLInputElement;
    const { name, value, type, checked } = target;
    setFormData(prev => ({ ...prev, [name]: type === "checkbox" ? checked : value }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    const msgs: Record<ActiveForm, string> = { signup: "Creating your account...", login: "Signing you in...", forgot: "Sending reset instructions...", reset: "Updating password..." };
    const toastId = toast.loading(msgs[activeForm]);
    try {
      if (activeForm === "signup") {
        if (formData.password !== formData.confirmPassword) throw new Error("Passwords do not match");
        if (!formData.agree) throw new Error("Please agree to Terms of Service");
        const { token, user } = await orgSignup({ email: formData.email, password: formData.password, name: formData.fullName, org_name: `${formData.fullName}'s Organisation` });
        localStorage.setItem("auth_token", token);
        localStorage.setItem("user", JSON.stringify(user));
        toast.update(toastId, { render: "Account created! Redirecting...", type: "success", isLoading: false, autoClose: 1500 });
        onAuthSuccess?.(token, user);
        setTimeout(() => { window.location.href = redirectTo || "/dashboard"; }, 300);
      } else if (activeForm === "login") {
        const { token, user } = await orgSignin({ email: formData.email, password: formData.password });
        localStorage.setItem("auth_token", token);
        localStorage.setItem("user", JSON.stringify(user));
        toast.update(toastId, { render: "Login successful! Redirecting...", type: "success", isLoading: false, autoClose: 1500 });
        onAuthSuccess?.(token, user);
        setTimeout(() => { window.location.href = redirectTo || "/dashboard"; }, 300);
      } else if (activeForm === "forgot") {
        await forgotPassword({ email: formData.email });
        toast.update(toastId, { render: "Password reset link sent! Check your inbox.", type: "success", isLoading: false, autoClose: 5000 });
      } else if (activeForm === "reset") {
        if (!formData.newPassword || formData.newPassword.length < 6) throw new Error("Password must be at least 6 characters.");
        if (formData.newPassword !== formData.confirmPassword) throw new Error("Passwords do not match.");
        await resetPassword({ token: formData.token || "", newPassword: formData.newPassword || "" });
        toast.update(toastId, { render: "Password reset! Redirecting to login...", type: "success", isLoading: false, autoClose: 2000 });
        setTimeout(() => { window.location.href = "/auth"; }, 2000);
      }
    } catch (err: any) {
      toast.update(toastId, { render: extractApiErrorMessage(err, "Authentication failed. Please try again."), type: "error", isLoading: false, autoClose: 4500 });
    } finally {
      setLoading(false);
    }
  };

  const isB2C = !!redirectTo;

  return (
    <div style={{ display: "flex", minHeight: "100vh", fontFamily: "'Inter', system-ui, sans-serif" }}>
      <style>{`
        .auth-brand { display: none; }
        @media (min-width: 900px) { .auth-brand { display: flex; } }
        .auth-form-panel { flex: 1; }
        .auth-back-link { display: inline-flex; align-items: center; gap: 6px; font-size: 13px; color: #64748b; cursor: pointer; border: none; background: transparent; padding: 0; margin-bottom: 28px; transition: color 0.15s; }
        .auth-back-link:hover { color: #0369A1; }
        .auth-input { width: 100%; height: 46px; border: 1.5px solid #e2e8f0; border-radius: 10px; padding: 0 14px; font-size: 14px; font-family: inherit; color: #0f172a; background: #f8fafc; outline: none; transition: border-color 0.18s, background 0.18s, box-shadow 0.18s; }
        .auth-input:focus { border-color: #0369A1; background: white; box-shadow: 0 0 0 3px rgba(3,105,161,0.1); }
        .auth-input::placeholder { color: #94a3b8; }
        .auth-label { font-size: 13px; font-weight: 500; color: #475569; margin-bottom: 6px; display: block; }
        .auth-submit { width: 100%; height: 46px; background: linear-gradient(135deg, #075985, #0369A1); color: white; border: none; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; font-family: inherit; transition: opacity 0.18s, box-shadow 0.18s; }
        .auth-submit:hover { opacity: 0.92; box-shadow: 0 8px 24px -6px rgba(3,105,161,0.4); }
        .auth-submit:active { opacity: 0.85; }
        .auth-link { color: #0369A1; cursor: pointer; font-weight: 500; }
        .auth-link:hover { text-decoration: underline; }
        .auth-divider { display: flex; align-items: center; gap: 12px; margin: 20px 0; color: #94a3b8; font-size: 12px; }
        .auth-divider::before, .auth-divider::after { content: ""; flex: 1; height: 1px; background: #e2e8f0; }
      `}</style>

      {/* ── LEFT: Brand panel ────────────────────────────── */}
      <div className="auth-brand" style={{ flex: "0 0 42%", background: "linear-gradient(145deg, #0C4A6E 0%, #075985 45%, #0369A1 100%)", flexDirection: "column", padding: "52px 44px", position: "relative", overflow: "hidden" }}>
        {/* Decorative circles */}
        <div style={{ position: "absolute", top: -100, right: -100, width: 400, height: 400, borderRadius: "50%", background: "rgba(255,255,255,0.04)", pointerEvents: "none" }} />
        <div style={{ position: "absolute", bottom: -80, left: -80, width: 320, height: 320, borderRadius: "50%", background: "rgba(255,255,255,0.03)", pointerEvents: "none" }} />
        {/* Dot grid */}
        <svg style={{ position: "absolute", inset: 0, width: "100%", height: "100%", pointerEvents: "none", opacity: 0.15 }}>
          <defs><pattern id="adg" width="28" height="28" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="1" fill="white" /></pattern></defs>
          <rect width="100%" height="100%" fill="url(#adg)" />
        </svg>

        {/* Logo mark */}
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 40, position: "relative", zIndex: 1 }}>
          <LogoIcon size={38} gradId="logo-left" />
          <div>
            <div style={{ fontSize: 17, fontWeight: 700, color: "white", letterSpacing: "-0.02em" }}>GenFrame</div>
            <div style={{ fontSize: 10, color: "rgba(255,255,255,0.55)", letterSpacing: "0.04em" }}>AI Image Adaptation</div>
          </div>
        </div>

        {/* Hero copy */}
        <div style={{ position: "relative", zIndex: 1, marginBottom: 36 }}>
          <div style={{ display: "inline-flex", alignItems: "center", gap: 6, background: "rgba(255,255,255,0.12)", borderRadius: 100, padding: "5px 12px", marginBottom: 20, border: "1px solid rgba(255,255,255,0.18)" }}>
            <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#34d399" }} />
            <span style={{ fontSize: 10, color: "rgba(255,255,255,0.85)", fontWeight: 500 }}>Free to try — no card needed</span>
          </div>

          {isB2C && activeForm === "signup" ? (
            <>
              <h2 style={{ fontSize: "clamp(22px,2.8vw,32px)", fontWeight: 700, color: "white", letterSpacing: "-0.03em", lineHeight: 1.2, marginBottom: 14 }}>
                Almost there!<br />Your images are<br /><span style={{ color: "rgba(255,255,255,0.55)" }}>ready to unlock.</span>
              </h2>
              <p style={{ fontSize: 14, color: "rgba(255,255,255,0.55)", lineHeight: 1.65, maxWidth: 320 }}>
                You've seen GenFrame in action. Create your free account and choose a plan to unlock every AI-adapted format at full resolution.
              </p>
            </>
          ) : (
            <>
              <h2 style={{ fontSize: "clamp(22px,2.8vw,32px)", fontWeight: 700, color: "white", letterSpacing: "-0.03em", lineHeight: 1.2, marginBottom: 14 }}>
                One upload.<br />Every platform.<br /><span style={{ color: "rgba(255,255,255,0.55)" }}>4 seconds.</span>
              </h2>
              <p style={{ fontSize: 14, color: "rgba(255,255,255,0.55)", lineHeight: 1.65, maxWidth: 320 }}>
                Upload one master image and get production-ready assets for Instagram, YouTube, LinkedIn and 44+ more in seconds.
              </p>
            </>
          )}
        </div>

        {/* Features list */}
        <div style={{ position: "relative", zIndex: 1, display: "flex", flexDirection: "column", gap: 12, marginBottom: 40 }}>
          {isB2C && activeForm === "signup" ? (
            /* B2C: show step-by-step progress */
            [
              { n: "1", label: "Try the AI", done: true },
              { n: "2", label: "Create your account", done: false, active: true },
              { n: "3", label: "Choose your plan", done: false },
            ].map((step, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <div style={{ width: 32, height: 32, borderRadius: "50%", background: step.done ? "rgba(16,185,129,0.25)" : step.active ? "rgba(255,255,255,0.2)" : "rgba(255,255,255,0.07)", border: step.done ? "1px solid rgba(16,185,129,0.5)" : step.active ? "1px solid rgba(255,255,255,0.4)" : "1px solid rgba(255,255,255,0.12)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, fontSize: 12, fontWeight: 700, color: step.done ? "#34d399" : "rgba(255,255,255,0.9)" }}>
                  {step.done ? "✓" : step.n}
                </div>
                <span style={{ fontSize: 13, color: step.done ? "rgba(52,211,153,0.9)" : step.active ? "white" : "rgba(255,255,255,0.4)", fontWeight: step.active ? 600 : 400, lineHeight: 1.4 }}>{step.label}</span>
                {step.active && <div style={{ marginLeft: "auto", background: "rgba(255,255,255,0.15)", borderRadius: 100, padding: "2px 8px", fontSize: 9, color: "rgba(255,255,255,0.8)", fontWeight: 600, letterSpacing: "0.05em" }}>NOW</div>}
              </div>
            ))
          ) : (
            BRAND_FEATURES.map((f, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <div style={{ width: 32, height: 32, borderRadius: 9, background: "rgba(255,255,255,0.1)", border: "1px solid rgba(255,255,255,0.15)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                  {f.icon}
                </div>
                <span style={{ fontSize: 13, color: "rgba(255,255,255,0.7)", lineHeight: 1.4 }}>{f.text}</span>
              </div>
            ))
          )}
        </div>

        {/* Social proof */}
        <div style={{ position: "relative", zIndex: 1, background: "rgba(255,255,255,0.07)", borderRadius: 14, padding: "16px 18px", border: "1px solid rgba(255,255,255,0.1)" }}>
          <div style={{ display: "flex", gap: 1, marginBottom: 8 }}>
            {[1,2,3,4,5].map(s => <span key={s} style={{ color: "#fbbf24", fontSize: 13 }}>★</span>)}
          </div>
          <p style={{ fontSize: 13, color: "rgba(255,255,255,0.7)", lineHeight: 1.6, marginBottom: 10 }}>
            "GenFrame saved our team 3 days per campaign. The AI just works."
          </p>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ width: 28, height: 28, borderRadius: "50%", background: "linear-gradient(135deg, #0891B2, #0EA5E9)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, color: "white", fontWeight: 600 }}>S</div>
            <div>
              <div style={{ fontSize: 12, color: "rgba(255,255,255,0.85)", fontWeight: 500 }}>Sarah M.</div>
              <div style={{ fontSize: 11, color: "rgba(255,255,255,0.45)" }}>Marketing Director</div>
            </div>
          </div>
        </div>
      </div>

      {/* ── RIGHT: Form panel ────────────────────────────── */}
      <div className="auth-form-panel" style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "clamp(32px, 5vw, 64px) clamp(20px, 5vw, 56px)", background: "white", overflowY: "auto" }}>
        <div style={{ width: "100%", maxWidth: 400 }}>
          {/* Back to home */}
          <button className="auth-back-link" onClick={() => router.push("/")}>
            <ArrowBackIcon sx={{ fontSize: 15 }} /> Back to home
          </button>

          {/* Logo */}
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 28 }}>
            <LogoIcon size={36} gradId="logo-right" />
            <div>
              <div style={{ fontSize: 17, fontWeight: 700, color: "#0f172a", letterSpacing: "-0.02em" }}>GenFrame</div>
              <div style={{ fontSize: 10, color: "#94a3b8", letterSpacing: "0.06em", textTransform: "uppercase" }}>AI Image Adaptation</div>
            </div>
          </div>

          {/* B2C anticipation banner */}
          {isB2C && activeForm === "signup" && (
            <div style={{ background: "linear-gradient(135deg, #f0fdf4, #dcfce7)", border: "1.5px solid #86efac", borderRadius: 14, padding: "14px 16px", marginBottom: 24 }}>
              {/* Step progress */}
              <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "center", gap: 4, marginBottom: 10 }}>
                {[
                  { label: "Try AI", done: true },
                  { label: "Create Account", active: true },
                  { label: "Choose Plan", upcoming: true },
                ].map((step, i) => (
                  <React.Fragment key={i}>
                    {i > 0 && (
                      <div style={{ flex: 1, height: 2, background: i === 1 ? "#86efac" : "#e2e8f0", margin: "10px 2px 0", minWidth: 16 }} />
                    )}
                    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
                      <div style={{ width: 22, height: 22, borderRadius: "50%", background: step.done ? "#10b981" : step.active ? "#0369A1" : "#e2e8f0", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, color: "white", fontWeight: 700, flexShrink: 0 }}>
                        {step.done ? "✓" : i + 1}
                      </div>
                      <span style={{ fontSize: 9, fontWeight: step.active ? 600 : 400, color: step.done ? "#10b981" : step.active ? "#0369A1" : "#94a3b8", whiteSpace: "nowrap" }}>
                        {step.label}
                      </span>
                    </div>
                  </React.Fragment>
                ))}
              </div>
              <p style={{ fontSize: 12, color: "#166534", fontWeight: 600, margin: 0, textAlign: "center" }}>
                Just one last step — you're one account away from unlocking your results
              </p>
            </div>
          )}

          {activeForm === "login"  && <LoginForm  formData={formData} handleChange={handleChange} handleSubmit={handleSubmit} switchForm={setActiveForm} />}
          {activeForm === "signup" && <SignupForm  formData={formData} handleChange={handleChange} handleSubmit={handleSubmit} switchForm={setActiveForm} />}
          {activeForm === "forgot" && <ForgotPasswordForm formData={formData} handleChange={handleChange} handleSubmit={handleSubmit} switchForm={setActiveForm} />}
          {activeForm === "reset"  && <ResetPasswordForm  formData={formData} handleChange={handleChange} handleSubmit={handleSubmit} switchForm={setActiveForm} />}
        </div>
      </div>
    </div>
  );
};

export default Auth;
