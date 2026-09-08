'use client';

import React from 'react';

import { ActiveForm } from '../Auth';

export interface ForgotPasswordProps {
  formData: {
    email: string;
  };
  handleChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
  handleSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  switchForm: React.Dispatch<React.SetStateAction<ActiveForm>>;
  loading?: boolean;
}

const ForgotPasswordForm: React.FC<ForgotPasswordProps> = ({
  formData,
  handleChange,
  handleSubmit,
  switchForm,
  loading,
}) => {
  return (
    <div style={{ width: '100%' }}>
      <h1 className="auth-title">Forgot password?</h1>
      <p className="auth-subtitle">Enter your email to reset your password</p>

      <form onSubmit={handleSubmit}>
        <div className="auth-field">
          <label className="auth-label" htmlFor="email">email</label>
          <input
            id="email"
            className="auth-input"
            name="email"
            type="email"
            placeholder="you@company.com"
            value={formData.email}
            onChange={handleChange}
            required
          />
        </div>

        <div style={{ marginTop: 8 }}>
          <button type="submit" className="auth-submit" disabled={loading}>
            {loading ? 'sending…' : 'continue'}
          </button>
        </div>

        <p className="auth-foot">
          <span className="auth-link" onClick={() => switchForm('login')}>back to sign in</span>
        </p>
      </form>
    </div>
  );
};

export default ForgotPasswordForm;
