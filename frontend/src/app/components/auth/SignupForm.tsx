'use client';

import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  InputAdornment,
  Button,
  FormControlLabel,
  Checkbox,
  IconButton,
} from '@mui/material';
import { Eye, EyeOff } from 'lucide-react';

import { ActiveForm } from '../Auth';

export interface FormProps {
  formData: {
    fullName: string;
    email: string;
    password: string;
    confirmPassword: string;
    agree: boolean;
  };
  handleChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
  handleSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  switchForm: React.Dispatch<React.SetStateAction<ActiveForm>>;
}

const SignupForm: React.FC<FormProps> = ({ formData, handleChange, handleSubmit, switchForm }) => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [passwordFocused, setPasswordFocused] = useState(false);
  const [confirmPasswordFocused, setConfirmPasswordFocused] = useState(false);

  const handleTogglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const handleToggleConfirmPasswordVisibility = () => {
    setShowConfirmPassword(!showConfirmPassword);
  };
  return (
    <Box
      sx={{
        width: '100%',
        maxWidth: 400,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
      }}
    >
      <Typography
        gutterBottom
        sx={{
          fontWeight: 600,
          fontSize: 30,
          lineHeight: '38px',
          textAlign: 'center',
        }}
      >
        Sign Up
      </Typography>

      <Typography
        gutterBottom
        sx={{
          fontWeight: 500,
          fontSize: 16,
          lineHeight: '24px',
          textAlign: 'center',
          mb: 2,
        }}
      >
        Enter the following details to sign up
      </Typography>

      <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
        {/* Full Name */}
        <Box sx={{ width: '100%', mb: 2 }}>
          <Typography
            sx={{
              fontFamily: 'Raleway',
              fontWeight: 500,
              fontSize: 14,
              lineHeight: '20px',
              color: 'rgba(69,69,69,1)',
              mb: 0.5,
            }}
          >
            Full Name
          </Typography>
          <TextField
            fullWidth
            name="fullName"
            placeholder="Enter full name"
            variant="outlined"
            value={formData.fullName}
            onChange={handleChange}
            required
            sx={{ '& .MuiOutlinedInput-root': { height: 48 } }}
          />
        </Box>

        {/* Email */}
        <Box sx={{ width: '100%', mb: 2 }}>
          <Typography
            component="label"
            htmlFor="email"
            sx={{
              fontFamily: 'Raleway',
              fontWeight: 500,
              fontSize: 14,
              lineHeight: '20px',
              color: 'rgba(69,69,69,1)',
              mb: 0.5,
              display: 'block',
            }}
          >
            Email
          </Typography>
          <TextField
            id="email"
            fullWidth
            name="email"
            type="email"
            placeholder="Enter email"
            variant="outlined"
            value={formData.email}
            onChange={handleChange}
            required
            sx={{ '& .MuiOutlinedInput-root': { height: 48 } }}
          />
        </Box>

        {/* Password */}
        <Box sx={{ width: '100%', mb: 2 }}>
          <Typography
            component="label"
            htmlFor="password"
            sx={{
              fontFamily: 'Raleway',
              fontWeight: 500,
              fontSize: 14,
              lineHeight: '20px',
              color: 'rgba(69,69,69,1)',
              mb: 0.5,
              display: 'block',
            }}
          >
            Password
          </Typography>
          <TextField
            id="password"
            fullWidth
            name="password"
            type={showPassword ? 'text' : 'password'}
            placeholder="Enter password"
            variant="outlined"
            value={formData.password}
            onChange={handleChange}
            onFocus={() => setPasswordFocused(true)}
            onBlur={() => setPasswordFocused(false)}
            required
            sx={{ '& .MuiOutlinedInput-root': { height: 48 } }}
            InputProps={{
              endAdornment: passwordFocused ? (
                <InputAdornment position="end">
                  <IconButton
                    onMouseDown={(e) => {
                      e.preventDefault();
                      handleTogglePasswordVisibility();
                    }}
                    edge="end"
                    sx={{ color: '#0369A1' }}
                  >
                    {showPassword ? (
                      <EyeOff size={20} />
                    ) : (
                      <Eye size={20} />
                    )}
                  </IconButton>
                </InputAdornment>
              ) : undefined,
            }}
          />
        </Box>

        {/* Confirm Password */}
        <Box sx={{ width: '100%', mb: 2 }}>
          <Typography
            component="label"
            htmlFor="confirmPassword"
            sx={{
              fontFamily: 'Raleway',
              fontWeight: 500,
              fontSize: 14,
              lineHeight: '20px',
              color: 'rgba(69,69,69,1)',
              mb: 0.5,
              display: 'block',
            }}
          >
            Confirm Password
          </Typography>
          <TextField
            id="confirmPassword"
            fullWidth
            name="confirmPassword"
            type={showConfirmPassword ? 'text' : 'password'}
            placeholder="Confirm password"
            variant="outlined"
            value={formData.confirmPassword}
            onChange={handleChange}
            onFocus={() => setConfirmPasswordFocused(true)}
            onBlur={() => setConfirmPasswordFocused(false)}
            required
            sx={{ '& .MuiOutlinedInput-root': { height: 48 } }}
            InputProps={{
              endAdornment: confirmPasswordFocused ? (
                <InputAdornment position="end">
                  <IconButton
                    onMouseDown={(e) => {
                      e.preventDefault();
                      handleToggleConfirmPasswordVisibility();
                    }}
                    edge="end"
                    sx={{ color: '#0369A1' }}
                  >
                    {showConfirmPassword ? (
                      <EyeOff size={20} />
                    ) : (
                      <Eye size={20} />
                    )}
                  </IconButton>
                </InputAdornment>
              ) : undefined,
            }}
          />
        </Box>

        {/* Terms */}
        <FormControlLabel
          control={
            <Checkbox
              name="agree"
              checked={formData.agree}
              onChange={handleChange}
              required
            />
          }
          label="I agree to the Terms of Service and Privacy Policy"
          sx={{
            fontFamily: 'Raleway',
            fontWeight: 500,
            fontSize: 12,
            lineHeight: '18px',
            mt: 1,
          }}
        />

        {/* Submit */}
        <Button
          type="submit"
          fullWidth
          variant="contained"
          sx={{
            mt: 3,
            mb: 2,
            backgroundColor: '#0369A1',
            borderRadius: 2,
          }}
        >
          Sign Up
        </Button>

        {/* Switch to Login */}
        <Typography variant="body2" align="center">
          Already have an account?{' '}
          <span
            onClick={() => switchForm('login')}
            style={{ color: '#0369A1', cursor: 'pointer' }}
          >
            Login
          </span>
        </Typography>
      </Box>
    </Box>
  );
};

export default SignupForm;
