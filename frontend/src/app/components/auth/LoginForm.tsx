'use client';

import React, { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';

import { ActiveForm } from '../Auth';

export interface FormProps {
  formData: {
    email: string;
    password: string;
  };
  handleChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
  handleSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  switchForm: React.Dispatch<React.SetStateAction<ActiveForm>>;
  loading?: boolean;
}

const LoginForm: React.FC<FormProps> = ({ formData, handleChange, handleSubmit, switchForm, loading }) => {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div style={{ width: '100%' }}>
      <h1 className="auth-title">Welcome back</h1>
      <p className="auth-subtitle">Enter your details to sign in</p>

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

        <div className="auth-field">
          <label className="auth-label" htmlFor="password">password</label>
          <div style={{ position: 'relative' }}>
            <input
              id="password"
              className="auth-input"
              style={{ paddingRight: 42 }}
              name="password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Enter password"
              value={formData.password}
              onChange={handleChange}
              required
            />
            <button type="button" className="auth-eye-btn" style={{ position: 'absolute', right: 6, top: '50%', transform: 'translateY(-50%)' }}
              onClick={() => setShowPassword(p => !p)} aria-label={showPassword ? 'Hide password' : 'Show password'}>
              {showPassword ? <EyeOff size={17} /> : <Eye size={17} />}
            </button>
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 20 }}>
          <span className="auth-link" style={{ fontSize: 12 }} onClick={() => switchForm('forgot')}>forgot password?</span>
        </div>

        <button type="submit" className="auth-submit" disabled={loading}>
          {loading ? 'signing in…' : 'sign in'}
        </button>

        <p className="auth-foot">
          Don't have an account? <span className="auth-link" onClick={() => switchForm('signup')}>sign up</span>
        </p>
      </form>
    </div>
  );
};

export default LoginForm;
