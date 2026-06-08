'use client';

import React from 'react';
import { Box, Typography, TextField, Button } from '@mui/material';

import { ActiveForm } from '../Auth';

export interface ForgotPasswordProps {
  formData: {
    email: string;
  };
  handleChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
  handleSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  switchForm: React.Dispatch<React.SetStateAction<ActiveForm>>;
}

const ForgotPasswordForm: React.FC<ForgotPasswordProps> = ({
  formData,
  handleChange,
  handleSubmit,
  switchForm,
}) => {
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
        Forgot Password?
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
        Enter your email to reset your password
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
          Continue
        </Button>

        {/* Back to Login */}
        <Typography
          variant="body2"
          align="center"
          sx={{ cursor: 'pointer', color: '#0369A1' }}
          onClick={() => switchForm('login')}
        >
          Back to Login
        </Typography>
      </Box>
    </Box>
  );
};

export default ForgotPasswordForm;
