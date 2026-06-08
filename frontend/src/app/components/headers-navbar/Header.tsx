"use client";
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  AppBar,
  Toolbar,
  Box,
  Button,
  Typography,
  useMediaQuery,
  useTheme,
  Menu,
  MenuItem,
  Avatar,
  Chip,
  IconButton,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Download as DownloadIcon,
  AutoAwesome as AutoAwesomeIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material';
import { useUser } from '@/app/context/AuthContext';
import { toast } from 'react-toastify';
import { extractApiErrorMessage } from '@/lib/errorMessage';

interface ProcessedImage {
  id: string;
  preset: string;
  url: string;
  ratio: string;
}

interface HeaderProps {
  processedImages?: ProcessedImage[];
}

// Header component
const Header = ({ processedImages = [] }: HeaderProps) => {
  const theme = useTheme();
  const router = useRouter();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { user } = useUser();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    router.push('/auth');
  };

  const handlePricing = () => {
    router.push('/pricing');
  };

  const handleGoBack = () => {
    if (typeof window !== 'undefined') {
      window.history.back();
    }
  };

  const handleDownloadAll = async () => {
    if (processedImages.length === 0) {
      toast.error('No images to download');
      return;
    }

    try {
      for (let i = 0; i < processedImages.length; i++) {
        const image = processedImages[i];
        const response = await fetch(image.url);
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `${image.preset}-${image.ratio}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(downloadUrl);

        // Small delay between downloads to prevent browser blocking
        if (i < processedImages.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 300));
        }
      }
    } catch (error) {
      console.error('Error downloading images:', error);
      toast.error(extractApiErrorMessage(error, 'Failed to download some images'));
    }
  };

  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        background: '#fff',
        minHeight: 80,
        boxShadow: 'none',
        color: 'text.primary',
        borderBottom: '1px solid #e5e7eb',
      }}
    >
      <Toolbar
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          px: { xs: 1.5, sm: 2.5, md: 6, lg: 8 },
          minHeight: { xs: 64, md: 80 },
          gap: { xs: 1, sm: 1.5 },
        }}
      >
        {/* Logo Section */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Box
            component="img"
            src="/logo.svg"
            alt="Logo"
            sx={{
              height: { xs: 32, md: 40 },
              width: 'auto',
            }}
          />
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography
              sx={{
                fontSize: { xs: '14px', md: '16px' },
                fontWeight: 500,
                color: '#6b7280',
                fontStyle: 'normal',
                display: { xs: 'none', md: 'block' },
                letterSpacing: '0.05em',
              }}
            >
              presents
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography
                variant="h6"
                sx={{
                  fontSize: { xs: '18px', sm: '18px', md: '20px' },
                  fontWeight: 600,
                  color: '#111827',
                  letterSpacing: '-0.03em',
                  display: { xs: 'none', sm: 'block' }
                }}
              >
                Visual Transformation Engine
              </Typography>
              <Typography
                variant="h6"
                sx={{
                  fontSize: '18px',
                  fontWeight: 600,
                  color: '#111827',
                  letterSpacing: '-0.03em',
                  display: { xs: 'block', sm: 'none' }
                }}
              >
                GenFrame
              </Typography>
            </Box>
          </Box>
        </Box>

        {/* Right Side Actions */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {/* Usage Stats */}
          {user && (
            <Chip
              label={(user.units ?? 0) >= (user.maxUnits ?? 1000) ? `LIMIT REACHED (${user.units}/${user.maxUnits})` : `${user.units ?? 0}/${user.maxUnits ?? 1000} credits`}
              onClick={() => router.push('/pricing')}
              color={(user.units ?? 0) >= (user.maxUnits ?? 1000) ? 'error' : 'default'}
              variant={(user.units ?? 0) >= (user.maxUnits ?? 1000) ? 'filled' : 'outlined'}
              sx={{
                fontWeight: 700,
                cursor: 'pointer',
                display: { xs: 'none', sm: 'flex' },
                '&:hover': {
                  opacity: 0.8
                }
              }}
            />
          )}

          {/* Download Button */}
          <Box sx={{ display: { xs: 'none', sm: 'block' } }}>
            <Button
              onClick={handleDownloadAll}
              disabled={processedImages.length === 0}
              startIcon={<DownloadIcon />}
              variant="contained"
              sx={{
                textTransform: 'none',
                bgcolor: 'rgba(3, 105, 161, 1)',
                color: 'white',
                fontSize: '14px',
                fontWeight: 700,
                borderRadius: '14px',
                boxShadow: '0 4px 12px rgba(3, 105, 161, 0.2)',
                '&:hover': {
                  bgcolor: 'rgba(3, 105, 161, 0.9)',
                  boxShadow: '0 6px 16px rgba(3, 105, 161, 0.3)',
                },
                px: 3,
                py: 1,
                minWidth: '140px'
              }}
            >
              Download All
            </Button>
          </Box>

          <Box sx={{ display: { xs: 'block', sm: 'none' } }}>
            <IconButton
              onClick={handleDownloadAll}
              disabled={processedImages.length === 0}
              sx={{
                bgcolor: processedImages.length === 0 ? '#f3f4f6' : 'rgba(3, 105, 161, 1)',
                color: processedImages.length === 0 ? '#9ca3af' : 'white',
                '&:hover': {
                  bgcolor: 'rgba(3, 105, 161, 0.9)',
                },
                width: 40,
                height: 40,
                borderRadius: '12px',
                boxShadow: processedImages.length === 0 ? 'none' : '0 4px 10px rgba(3, 105, 161, 0.2)'
              }}
            >
              <DownloadIcon sx={{ fontSize: 20 }} />
            </IconButton>
          </Box>

          {/* Pricing Button */}
          <Button
            onClick={handlePricing}
            variant="outlined"
            sx={{
              textTransform: 'none',
                borderColor: 'rgba(3, 105, 161, 1)',
                color: 'rgba(3, 105, 161, 1)',
              fontSize: { xs: '13px', md: '14px' },
              fontWeight: 600,
              borderRadius: '12px',
              px: { xs: 1.5, md: 2.5 },
              py: { xs: 0.8, md: 1 },
              display: { xs: 'none', sm: 'block' }
            }}
          >
            Pricing
          </Button>

          {/* User Menu */}
          {user ? (
            <>
              <Button
                onClick={handleMenuOpen}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                  textTransform: 'none',
                  color: 'text.primary',
                  padding: '4px 8px',
                  '&:hover': {
                    backgroundColor: '#f3f4f6',
                  },
                }}
              >
                <Avatar
                  sx={{
                    width: 32,
                    height: 32,
                    backgroundColor: 'rgba(3, 105, 161, 1)',
                    fontSize: '14px',
                    fontWeight: 600,
                  }}
                >
                  {user.email.charAt(0).toUpperCase()}
                </Avatar>
                <Typography
                  sx={{
                    display: { xs: 'none', md: 'block' },
                    fontSize: '13px',
                    fontWeight: 500,
                  }}
                >
                  {user.fullName || user.email}
                </Typography>
              </Button>
              <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
              >
                <MenuItem disabled>
                  <Typography variant="caption">Plan: {user.plan}</Typography>
                </MenuItem>
                <MenuItem onClick={handleLogout}>
                  <LogoutIcon sx={{ mr: 1, fontSize: 20 }} />
                  <Typography>Logout</Typography>
                </MenuItem>
              </Menu>
            </>
          ) : (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <Button
                onClick={() => router.push('/auth')}
                sx={{
                  textTransform: 'none',
                  color: '#4b5563',
                  fontSize: '14px',
                  fontWeight: 600,
                  '&:hover': {
                    bgcolor: 'transparent',
                    color: 'rgba(3, 105, 161, 1)',
                  },
                }}
              >
                Login
              </Button>
              <Button
                onClick={() => router.push('/auth?mode=signup')}
                variant="contained"
                sx={{
                  textTransform: 'none',
                  bgcolor: 'rgba(3, 105, 161, 1)',
                  color: 'white',
                  fontSize: '14px',
                  fontWeight: 600,
                  borderRadius: '12px',
                  px: 3,
                  py: 1,
                  '&:hover': {
                    bgcolor: 'rgba(3, 105, 161, 0.9)',
                  },
                }}
              >
                Sign Up
              </Button>
            </Box>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;

