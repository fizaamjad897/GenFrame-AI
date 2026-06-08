'use client';

import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  InputAdornment,
  Button,
  Link,
  IconButton,
} from '@mui/material';
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
}

const LoginForm: React.FC<FormProps> = ({ formData, handleChange, handleSubmit, switchForm }) => {
  const [showPassword, setShowPassword] = useState(false);
  const [passwordFocused, setPasswordFocused] = useState(false);

  const handleTogglePasswordVisibility = () => {
    setShowPassword(!showPassword);
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
      <Box>
        <img
          src="/logo.svg"
          alt="GenFrame Logo"
          style={{ width: 210, height: 64, marginBottom: 20 }}
        />
      </Box>

      <Typography
        gutterBottom
        sx={{
          fontWeight: 600,
          fontSize: 30,
          lineHeight: '38px',
          textAlign: 'center',
        }}
      >
        Welcome Back!
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
        Enter the following details to login
      </Typography>

      <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
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

        {/* Forgot Password */}
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'flex-end',
            mb: 2,
          }}
        >
          <Typography
            sx={{
              fontFamily: 'Raleway',
              fontWeight: 500,
              fontSize: 14,
              lineHeight: '20px',
              color: '#0369A1',
              cursor: 'pointer',
            }}
            onClick={() => switchForm('forgot')}
          >
            Forgot Password?
          </Typography>
        </Box>

        {/* Submit */}
        <Button
          type="submit"
          fullWidth
          variant="contained"
          sx={{
            mt: 1,
            mb: 2,
            backgroundColor: '#0369A1',
            borderRadius: 2,
          }}
        >
          Login
        </Button>

        {/* Switch to Signup 
        <Typography variant="body2" align="center">
          Don't have an account?{' '}
          <span
            onClick={() => switchForm('signup')}
            style={{ color: 'rgba(3, 105, 161,1)', cursor: 'pointer' }}
          >
            Sign up
          </span>
        </Typography>
        */}
      </Box>
    </Box>
  );
};

export default LoginForm;
