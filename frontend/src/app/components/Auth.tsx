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
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import BoltIcon from "@mui/icons-material/Bolt";
import GridViewIcon from "@mui/icons-material/GridView";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import { useRouter } from "next/navigation";
import { CREAM, INK, PANEL_LINE, TEXT_MUTED_D, TEXT_MUTED_L, BORDER_D, BORDER_L, ACCENT, ACCENT_SOFT, SHADOW_SM, DISPLAY, BODY, MONO } from "../theme/terminal";
import GridMark from "../theme/GridMark";

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

const BRAND_FEATURES = [
  { icon: <AutoAwesomeIcon sx={{ fontSize: 15 }} />, text: "47+ platform format specs included" },
  { icon: <BoltIcon sx={{ fontSize: 15 }} />, text: "AI adaptation in under 4 seconds" },
  { icon: <GridViewIcon sx={{ fontSize: 15 }} />, text: "Full resolution export, no watermarks" },
  { icon: <CheckCircleIcon sx={{ fontSize: 15 }} />, text: "Works for Instagram, YouTube, LinkedIn & 44 more" },
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
    <div style={{ display: "flex", minHeight: "100vh", fontFamily: BODY, background: CREAM }}>
      <style>{`
        .auth-brand { display: none; }
        @media (min-width: 900px) { .auth-brand { display: flex; } }
        .auth-form-panel { flex: 1; }
        .auth-back-link { display: inline-flex; align-items: center; gap: 6px; font-family: ${BODY}; font-size: 13px; font-weight: 500; color: ${TEXT_MUTED_L}; cursor: pointer; border: none; background: transparent; padding: 0; margin-bottom: 28px; transition: color 0.15s; }
        .auth-back-link:hover { color: ${ACCENT}; }
        .auth-input { width: 100%; height: 48px; border: 1px solid ${BORDER_L}; border-radius: 12px; padding: 0 16px; font-family: ${BODY}; font-size: 15px; font-weight: 400; color: ${INK}; background: transparent; outline: none; transition: border-color 0.15s, box-shadow 0.15s; }
        .auth-input:focus { border-color: ${ACCENT}; box-shadow: 0 0 0 3px ${ACCENT_SOFT}; }
        .auth-input::placeholder { color: ${TEXT_MUTED_L}; }
        .auth-label { font-family: ${BODY}; font-size: 13.5px; font-weight: 500; color: ${INK}; margin-bottom: 7px; display: block; letter-spacing: 0; }
        .auth-submit { width: 100%; height: 50px; background: linear-gradient(135deg, #A78BFA, ${ACCENT}); color: #FFFFFF; border: none; border-radius: 12px; font-family: ${BODY}; font-size: 15px; font-weight: 500; cursor: pointer; transition: filter 0.15s, box-shadow 0.15s; box-shadow: ${SHADOW_SM}; }
        .auth-submit:hover { filter: brightness(1.04); }
        .auth-submit:disabled { opacity: 0.55; cursor: not-allowed; }
        .auth-link { color: ${ACCENT}; cursor: pointer; font-weight: 500; }
        .auth-link:hover { text-decoration: underline; }
        .auth-eye-btn { background: transparent; border: none; cursor: pointer; color: ${TEXT_MUTED_L}; display: flex; align-items: center; padding: 4px; }
        .auth-eye-btn:hover { color: ${ACCENT}; }
        .auth-title { font-family: ${DISPLAY}; font-size: clamp(28px,3.4vw,36px); font-weight: 500; letter-spacing: -0.02em; color: ${INK}; text-align: center; margin: 0 0 10px; }
        .auth-subtitle { font-family: ${BODY}; font-size: 15px; color: ${TEXT_MUTED_L}; text-align: center; margin: 0 0 30px; line-height: 1.55; }
        .auth-field { width: 100%; margin-bottom: 18px; }
        .auth-foot { font-family: ${BODY}; font-size: 13.5px; color: ${TEXT_MUTED_L}; text-align: center; margin-top: 20px; }
        .auth-checkbox-row { display: flex; align-items: flex-start; gap: 8px; margin: 4px 0 22px; }
        .auth-checkbox-row input { accent-color: ${ACCENT}; margin-top: 2px; }
        .auth-checkbox-row label { font-family: ${BODY}; font-size: 13px; color: ${TEXT_MUTED_L}; line-height: 1.5; }
      `}</style>

      {/* ── LEFT: Brand panel ────────────────────────────── */}
      <div className="auth-brand" style={{ flex: "0 0 42%", background: INK, flexDirection: "column", padding: "52px 44px", position: "relative", overflow: "hidden" }}>
        {/* Logo mark */}
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 44, position: "relative", zIndex: 1 }}>
          <GridMark size={34} />
          <div>
            <div style={{ fontFamily: DISPLAY, fontSize: 17, fontWeight: 500, color: CREAM }}>Recreative AI</div>
            <div style={{ fontFamily: MONO, fontSize: 11, color: TEXT_MUTED_D }}>ai image adaptation</div>
          </div>
        </div>

        {/* Hero copy */}
        <div style={{ position: "relative", zIndex: 1, marginBottom: 36 }}>
          <div style={{ display: "inline-flex", alignItems: "center", gap: 8, border: `1px solid ${BORDER_D}`, borderRadius: 12, padding: "5px 12px", marginBottom: 22 }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: ACCENT }} />
            <span style={{ fontFamily: MONO, fontSize: 12, color: TEXT_MUTED_D }}>free to try — no card needed</span>
          </div>

          {isB2C && activeForm === "signup" ? (
            <>
              <h2 style={{ fontFamily: DISPLAY, fontSize: "clamp(26px,3vw,34px)", fontWeight: 500, color: CREAM, letterSpacing: "-0.02em", lineHeight: 1.2, marginBottom: 14 }}>
                Almost there.<br />Every format is<br /><span style={{ color: ACCENT }}>ready to unlock.</span>
              </h2>
              <p style={{ fontFamily: BODY, fontSize: 14.5, color: TEXT_MUTED_D, lineHeight: 1.6, maxWidth: 320 }}>
                You've seen Recreative AI in action. Create your account and choose a plan to unlock every panel at full resolution.
              </p>
            </>
          ) : (
            <>
              <h2 style={{ fontFamily: DISPLAY, fontSize: "clamp(26px,3vw,34px)", fontWeight: 500, color: CREAM, letterSpacing: "-0.02em", lineHeight: 1.2, marginBottom: 14 }}>
                One upload.<br />Every exact <span style={{ color: ACCENT }}>spec.</span>
              </h2>
              <p style={{ fontFamily: BODY, fontSize: 14.5, color: TEXT_MUTED_D, lineHeight: 1.6, maxWidth: 320 }}>
                Upload one master image and get production-ready panels for 47+ real OOH and platform specs in seconds.
              </p>
            </>
          )}
        </div>

        {/* Features / step progress */}
        <div style={{ position: "relative", zIndex: 1, display: "flex", flexDirection: "column", gap: 12, marginBottom: 40 }}>
          {isB2C && activeForm === "signup" ? (
            [
              { n: "1", label: "Try the AI", done: true },
              { n: "2", label: "Create your account", active: true },
              { n: "3", label: "Choose your plan" },
            ].map((step, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <div style={{ width: 26, height: 26, border: `1px solid ${step.done ? "#10B981" : step.active ? ACCENT : BORDER_D}`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, fontFamily: BODY, fontSize: 12, fontWeight: 500, color: step.done ? "#10B981" : step.active ? ACCENT : TEXT_MUTED_D }}>
                  {step.done ? "✓" : step.n}
                </div>
                <span style={{ fontFamily: MONO, fontSize: 12, color: step.done ? "#10B981" : step.active ? CREAM : TEXT_MUTED_D, fontWeight: step.active ? 500 : 400 }}>{step.label}</span>
                {step.active && <span style={{ marginLeft: "auto", fontFamily: MONO, fontSize: 11, color: ACCENT, border: `1px solid ${ACCENT}`, padding: "2px 7px" }}>NOW</span>}
              </div>
            ))
          ) : (
            BRAND_FEATURES.map((f, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <div style={{ width: 30, height: 30, border: `1px solid ${BORDER_D}`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, color: ACCENT }}>
                  {f.icon}
                </div>
                <span style={{ fontFamily: BODY, fontSize: 14, color: TEXT_MUTED_D, lineHeight: 1.45 }}>{f.text}</span>
              </div>
            ))
          )}
        </div>

        {/* Social proof */}
        <div style={{ position: "relative", zIndex: 1, border: `1px solid ${BORDER_D}`, borderRadius: 12, padding: "16px 18px" }}>
          <div style={{ fontFamily: MONO, fontSize: 11.5, color: ACCENT, marginBottom: 8 }}>★★★★★</div>
          <p style={{ fontFamily: BODY, fontSize: 14, color: TEXT_MUTED_D, lineHeight: 1.55, marginBottom: 10 }}>
            "Recreative AI saved our team 3 days per campaign. It just works."
          </p>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ width: 26, height: 26, background: ACCENT, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: BODY, fontSize: 12, color: "#FFFFFF", fontWeight: 500 }}>S</div>
            <div>
              <div style={{ fontFamily: BODY, fontSize: 12, color: CREAM, fontWeight: 500 }}>Sarah M.</div>
              <div style={{ fontFamily: MONO, fontSize: 11.5, color: TEXT_MUTED_D }}>marketing director</div>
            </div>
          </div>
        </div>
      </div>

      {/* ── RIGHT: Form panel ────────────────────────────── */}
      <div className="auth-form-panel" style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "clamp(32px, 5vw, 64px) clamp(20px, 5vw, 56px)", background: CREAM, overflowY: "auto" }}>
        <div style={{ width: "100%", maxWidth: 380 }}>
          <button className="auth-back-link" onClick={() => router.push("/")}>
            <ArrowBackIcon sx={{ fontSize: 14 }} /> back to home
          </button>

          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 28 }}>
            <GridMark size={30} />
            <div>
              <div style={{ fontFamily: DISPLAY, fontSize: 17, fontWeight: 500, color: INK }}>Recreative AI</div>
              <div style={{ fontFamily: MONO, fontSize: 11, color: TEXT_MUTED_L }}>ai image adaptation</div>
            </div>
          </div>

          {isB2C && activeForm === "signup" && (
            <div style={{ border: `1px solid ${ACCENT}`, borderRadius: 12, padding: "14px 16px", marginBottom: 24 }}>
              <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "center", gap: 4, marginBottom: 10 }}>
                {[
                  { label: "Try AI", done: true },
                  { label: "Create Account", active: true },
                  { label: "Choose Plan" },
                ].map((step, i) => (
                  <React.Fragment key={i}>
                    {i > 0 && <div style={{ flex: 1, height: 1, background: i === 1 ? ACCENT : BORDER_L, margin: "9px 2px 0", minWidth: 16 }} />}
                    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
                      <div style={{ width: 20, height: 20, border: `1px solid ${step.done ? "#10B981" : step.active ? ACCENT : BORDER_L}`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: BODY, fontSize: 11.5, color: step.done ? "#10B981" : step.active ? ACCENT : TEXT_MUTED_L, fontWeight: 500, flexShrink: 0 }}>
                        {step.done ? "✓" : i + 1}
                      </div>
                      <span style={{ fontFamily: MONO, fontSize: 12, fontWeight: step.active ? 500 : 400, color: step.done ? "#10B981" : step.active ? ACCENT : TEXT_MUTED_L, whiteSpace: "nowrap" }}>{step.label}</span>
                    </div>
                  </React.Fragment>
                ))}
              </div>
              <p style={{ fontFamily: BODY, fontSize: 12.5, color: INK, fontWeight: 500, margin: 0, textAlign: "center" }}>
                one last step — you're one account away
              </p>
            </div>
          )}

          {activeForm === "login" && <LoginForm formData={formData} handleChange={handleChange} handleSubmit={handleSubmit} switchForm={setActiveForm} loading={loading} />}
          {activeForm === "signup" && <SignupForm formData={formData} handleChange={handleChange} handleSubmit={handleSubmit} switchForm={setActiveForm} loading={loading} />}
          {activeForm === "forgot" && <ForgotPasswordForm formData={formData} handleChange={handleChange} handleSubmit={handleSubmit} switchForm={setActiveForm} loading={loading} />}
          {activeForm === "reset" && <ResetPasswordForm formData={formData} handleChange={handleChange} handleSubmit={handleSubmit} switchForm={setActiveForm} loading={loading} />}
        </div>
      </div>
    </div>
  );
};

export default Auth;
