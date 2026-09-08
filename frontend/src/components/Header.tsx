"use client";
import React from 'react';
import {
  AppBar,
  Toolbar,
  Box,
  Button,
  Typography,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Download as DownloadIcon,
  AutoAwesome as AutoAwesomeIcon
} from '@mui/icons-material';
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

const Header = ({ processedImages = [] }: HeaderProps) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

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
        boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        color: 'text.primary',
        borderBottom: '1px solid #e5e7eb',
      }}
    >
      <Toolbar
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          px: { xs: 2, sm: 3, md: 6, lg: 8 },
          minHeight: { xs: 64, md: 80 },
          gap: 1,
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
                  fontSize: { xs: '18px', md: '20px' },
                  fontWeight: 500,
                  color: '#111827',
                  letterSpacing: '-0.01em',
                }}
              >
                Visual Transformation Engine
              </Typography>
            </Box>
          </Box>
        </Box>

        {/* Right Side Actions */}
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Button
            onClick={handleDownloadAll}
            disabled={processedImages.length === 0}
            startIcon={<DownloadIcon />}
            variant="contained"
            sx={{
              textTransform: 'none',
              bgcolor: 'rgba(74, 0, 224, 1)',
              color: 'white',
              fontSize: { xs: '13px', md: '14px' },
              fontWeight: 500,
              borderRadius: '18px',
              '&:hover': {
                bgcolor: 'rgba(74, 0, 224, 0.9)',
              },
              '&.Mui-disabled': {
                bgcolor: '#f3f4f6',
                color: '#9ca3af',
              },
              px: { xs: 1.5, md: 3 },
              py: { xs: 0.8, md: 1.2 },
              minWidth: { xs: 'auto', md: '140px' },
              '& .MuiButton-startIcon': {
                marginRight: { xs: 0, md: 1 },
                marginLeft: { xs: 0, md: -0.5 }
              }
            }}
          >
            <Box component="span" sx={{ display: { xs: 'none', md: 'inline' } }}>
              Download All
            </Box>
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;

