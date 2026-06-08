"use client";

import React, { useState } from "react";
import {
  Box,
  Typography,
  TextField,
  Button,
  InputAdornment,
  IconButton,
} from "@mui/material";
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
}

const ResetPasswordForm: React.FC<FormProps> = ({
  formData,
  handleChange,
  handleSubmit,
  switchForm,
}) => {
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [newPasswordFocused, setNewPasswordFocused] = useState(false);

  const handleToggleNewPasswordVisibility = () => {
    setShowNewPassword(!showNewPassword);
  };
  return (
    <Box
      sx={{
        width: "100%",
        maxWidth: 400,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
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
          lineHeight: "38px",
          textAlign: "center",
        }}
      >
        Reset Password
      </Typography>

      <Typography
        gutterBottom
        sx={{
          fontWeight: 500,
          fontSize: 16,
          lineHeight: "24px",
          textAlign: "center",
          mb: 2,
        }}
      >
        Enter the following details to reset password
      </Typography>

      <Box component="form" onSubmit={handleSubmit} sx={{ width: "100%" }}>
        {/* NEW PASSWORD */}
        <Box sx={{ width: "100%", mb: 2 }}>
          <Typography
            component="label"
            htmlFor="newPassword"
            sx={{
              fontFamily: "Raleway",
              fontWeight: 500,
              fontSize: 14,
              lineHeight: "20px",
              color: "rgba(69,69,69,1)",
              mb: 0.5,
              display: "block",
            }}
          >
            New Password
          </Typography>
          <TextField
            id="newPassword"
            fullWidth
            name="newPassword"
            type={showNewPassword ? "text" : "password"}
            placeholder="Enter new password"
            variant="outlined"
            value={formData.newPassword || ""}
            onChange={handleChange}
            onFocus={() => setNewPasswordFocused(true)}
            onBlur={() => setNewPasswordFocused(false)}
            required
            sx={{ "& .MuiOutlinedInput-root": { height: 48 } }}
            InputProps={{
              endAdornment: newPasswordFocused ? (
                <InputAdornment position="end">
                  <IconButton
                    onMouseDown={(e) => {
                      e.preventDefault();
                      handleToggleNewPasswordVisibility();
                    }}
                    edge="end"
                    sx={{ color: "#0369A1" }}
                  >
                    {showNewPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </IconButton>
                </InputAdornment>
              ) : undefined,
            }}
          />
        </Box>

        {/* CONFIRM PASSWORD */}
        <Box sx={{ width: "100%", mb: 2 }}>
          <Typography
            component="label"
            htmlFor="confirmPassword"
            sx={{
              fontFamily: "Raleway",
              fontWeight: 500,
              fontSize: 14,
              lineHeight: "20px",
              color: "rgba(69,69,69,1)",
              mb: 0.5,
              display: "block",
            }}
          >
            Confirm Password
          </Typography>
          <TextField
            id="confirmPassword"
            fullWidth
            name="confirmPassword"
            type={showNewPassword ? "text" : "password"}
            placeholder="Re-enter new password"
            variant="outlined"
            value={formData.confirmPassword || ""}
            onChange={handleChange}
            onFocus={() => setNewPasswordFocused(true)}
            onBlur={() => setNewPasswordFocused(false)}
            required
            sx={{ "& .MuiOutlinedInput-root": { height: 48 } }}
            InputProps={{
              endAdornment: newPasswordFocused ? (
                <InputAdornment position="end">
                  <IconButton
                    onMouseDown={(e) => {
                      e.preventDefault();
                      handleToggleNewPasswordVisibility();
                    }}
                    edge="end"
                    sx={{ color: "#0369A1" }}
                  >
                    {showNewPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </IconButton>
                </InputAdornment>
              ) : undefined,
            }}
          />
        </Box>

        {/* Submit */}
        <Button
          type="submit"
          fullWidth
          variant="contained"
          sx={{
            mt: 1,
            mb: 2,
            backgroundColor: "#0369A1",
            borderRadius: 2,
          }}
        >
          Confirm
        </Button>
      </Box>
    </Box>
  );
};

export default ResetPasswordForm;
