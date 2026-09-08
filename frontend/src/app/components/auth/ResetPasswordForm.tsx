"use client";

import React, { useState } from "react";
import { Eye, EyeOff } from "lucide-react";

import { ActiveForm } from "../Auth";

export interface FormProps {
  formData: {
    email: string;
    password: string;
    token?: string;
    newPassword?: string;
    confirmPassword?: string;
  };
  handleChange: (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => void;
  handleSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  switchForm: React.Dispatch<React.SetStateAction<ActiveForm>>;
  loading?: boolean;
}

const ResetPasswordForm: React.FC<FormProps> = ({
  formData,
  handleChange,
  handleSubmit,
  loading,
}) => {
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  return (
    <div style={{ width: "100%" }}>
      <h1 className="auth-title">Reset password</h1>
      <p className="auth-subtitle">Enter your new password below</p>

      <form onSubmit={handleSubmit}>
        <div className="auth-field">
          <label className="auth-label" htmlFor="newPassword">new password</label>
          <div style={{ position: "relative" }}>
            <input
              id="newPassword"
              className="auth-input"
              style={{ paddingRight: 42 }}
              name="newPassword"
              type={showNewPassword ? "text" : "password"}
              placeholder="Enter new password"
              value={formData.newPassword || ""}
              onChange={handleChange}
              required
            />
            <button type="button" className="auth-eye-btn" style={{ position: "absolute", right: 6, top: "50%", transform: "translateY(-50%)" }}
              onClick={() => setShowNewPassword(p => !p)} aria-label={showNewPassword ? "Hide password" : "Show password"}>
              {showNewPassword ? <EyeOff size={17} /> : <Eye size={17} />}
            </button>
          </div>
        </div>

        <div className="auth-field">
          <label className="auth-label" htmlFor="confirmPassword">confirm password</label>
          <div style={{ position: "relative" }}>
            <input
              id="confirmPassword"
              className="auth-input"
              style={{ paddingRight: 42 }}
              name="confirmPassword"
              type={showConfirmPassword ? "text" : "password"}
              placeholder="Re-enter new password"
              value={formData.confirmPassword || ""}
              onChange={handleChange}
              required
            />
            <button type="button" className="auth-eye-btn" style={{ position: "absolute", right: 6, top: "50%", transform: "translateY(-50%)" }}
              onClick={() => setShowConfirmPassword(p => !p)} aria-label={showConfirmPassword ? "Hide password" : "Show password"}>
              {showConfirmPassword ? <EyeOff size={17} /> : <Eye size={17} />}
            </button>
          </div>
        </div>

        <button type="submit" className="auth-submit" disabled={loading}>
          {loading ? "updating…" : "confirm"}
        </button>
      </form>
    </div>
  );
};

export default ResetPasswordForm;
