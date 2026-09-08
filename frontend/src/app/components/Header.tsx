"use client";
import React from "react";
import {
  AppBar,
  Toolbar,
  Box,
  Button,
  Typography,
  useMediaQuery,
  useTheme,
  Avatar,
  IconButton,
  Menu,
  MenuItem,
  Tooltip,
} from "@mui/material";
import {
  Download as DownloadIcon,
  Logout as LogoutIcon,
  Person as PersonIcon,
  CreditCard as CreditCardIcon,
  Insights as InsightsIcon,
  Star as StarIcon,
  PhotoLibrary as PhotoLibraryIcon,
  AutoAwesome as AutoAwesomeIcon,
} from "@mui/icons-material";
import { useUser } from "@/app/context/AuthContext";
import { useRouter, usePathname } from "next/navigation";
import { toast } from "react-toastify";
import { extractApiErrorMessage } from "@/lib/errorMessage";

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
  const { user, logout } = useUser();
  const router = useRouter();
  const pathname = usePathname();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);

  const handleOpenUserMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleCloseUserMenu = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    handleCloseUserMenu();
    await logout();
    router.push("/auth");
  };

  const handleDownloadAll = async () => {
    if (processedImages.length === 0) {
      toast.error("No images to download");
      return;
    }

    try {
      for (let i = 0; i < processedImages.length; i++) {
        const image = processedImages[i];
        const response = await fetch(image.url);
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = downloadUrl;
        link.download = `${image.preset}-${image.ratio}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(downloadUrl);

        // Small delay between downloads to prevent browser blocking
        if (i < processedImages.length - 1) {
          await new Promise((resolve) => setTimeout(resolve, 300));
        }
      }
    } catch (error) {
      console.error("Error downloading images:", error);
      toast.error(extractApiErrorMessage(error, "Failed to download some images"));
    }
  };

  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        background: "#FFFFFF",
        minHeight: { xs: 60, md: 72 },
        boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
        color: "text.primary",
        borderBottom: "1px solid #E5E7EB",
        zIndex: (theme) => theme.zIndex.drawer + 1,
      }}
    >
      <Toolbar
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          px: { xs: 1.5, sm: 3 },
          minHeight: { xs: 60, md: 72 },
        }}
      >
        <Box
          sx={{
            width: "100%",
            maxWidth: "1600px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: 2,
          }}
        >
          {/* Logo Section */}
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              gap: 1.5,
              cursor: "pointer",
              "&:hover": { opacity: 0.85 },
              transition: "opacity 0.2s",
            }}
            onClick={() => router.push("/")}
          >
            <Box
              sx={{
                width: 32,
                height: 32,
                borderRadius: "18px",
                background: "#8B5CF6",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
                boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
              }}
            >
              <AutoAwesomeIcon sx={{ fontSize: 15, color: "#111827" }} />
            </Box>
            <Box
              sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "flex-start",
              }}
            >
              <Typography
                sx={{
                  fontSize: { xs: "14px", md: "15px" },
                  fontWeight: 600,
                  color: "#111827",
                  letterSpacing: "-0.02em",
                  lineHeight: 1.1,
                }}
              >
                Recreative AI
              </Typography>
              <Typography
                sx={{
                  fontSize: "9px",
                  fontWeight: 500,
                  color: "#9CA3AF",
                  letterSpacing: "0.02em",
                  lineHeight: 1,
                }}
              >
                AI Image Adaptation
              </Typography>
            </Box>
          </Box>

          <Box sx={{ display: "flex", alignItems: "center", gap: 2, flex: 1, justifyContent: "center" }}>
            {/* Navigation Links */}
            <Box sx={{ display: { xs: "none", md: "flex" }, gap: 1.25, alignItems: "center", flexWrap: "wrap", justifyContent: "center" }}>
              {user && (
                <>
                  {[
                    { label: "Home", path: "/dashboard" },
                    { label: "Billing", path: "/billing" },
                    { label: "Archive", path: "/archive" },
                    { label: "Design Analytics", path: "/reports", icon: <InsightsIcon sx={{ fontSize: 15 }} /> },
                  ].map((item) => {
                    const active = pathname === item.path;
                    const isAnalytics = item.path === "/reports";
                    return (
                      <Button
                        key={item.path}
                        onClick={() => router.push(item.path)}
                        startIcon={item.icon}
                        sx={{
                          textTransform: "none",
                          borderRadius: "18px",
                          px: isAnalytics ? 2.2 : 1.6,
                          py: 0.9,
                          minHeight: 38,
                          color: active ? "#8B5CF6" : "#57534A",
                          fontWeight: 600,
                          fontSize: "13px",
                          border: active ? "1px solid #8B5CF6" : "1px solid transparent",
                          bgcolor: "transparent",
                          boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
                          "&:hover": {
                            bgcolor: "rgba(139, 92, 246, 0.06)",
                            borderColor: "rgba(139, 92, 246, 0.3)",
                          },
                        }}
                      >
                        {item.label}
                      </Button>
                    );
                  })}
                </>
              )}
            </Box>
          </Box>

          {/* Right Side Actions */}
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              gap: { xs: 1.25, sm: 1.5, md: 2 },
            }}
          >
            {pathname !== "/pricing" && (
              <Box sx={{ display: { xs: "none", sm: "block" } }}>
                <Button
                  onClick={() => router.push("/reports")}
                  variant="outlined"
                  startIcon={<InsightsIcon sx={{ fontSize: 17 }} />}
                  sx={{
                    textTransform: "none",
                    borderRadius: "18px",
                    px: 2,
                    py: 0.9,
                    height: 40,
                    borderColor: "#8B5CF6",
                    borderStyle: "solid",
                    color: "#8B5CF6",
                    fontWeight: 600,
                    bgcolor: "transparent",
                    "&:hover": {
                      borderColor: "#8B5CF6",
                      bgcolor: "rgba(139, 92, 246, 0.06)",
                    },
                  }}
                >
                  Design Analytics
                </Button>
                {/* <Button
                  onClick={handleDownloadAll}
                  disabled={processedImages.length === 0}
                  startIcon={<DownloadIcon sx={{ fontSize: 18 }} />}
                  variant="contained"
                  sx={{
                    textTransform: 'none',
                    bgcolor: 'rgba(139, 92, 246, 1)',
                    color: 'white',
                    fontSize: '12.5px',
                    fontWeight: 500,
                    borderRadius: '8px',
                    boxShadow: '0 4px 12px rgba(139, 92, 246, 0.2)',
                    '&:hover': {
                      bgcolor: 'rgba(139, 92, 246, 0.9)',
                      boxShadow: '0 6px 16px rgba(139, 92, 246, 0.3)',
                    },
                    px: 2,
                    py: 0.75,
                    minWidth: '110px'
                  }}
                >
                  Download All
                </Button> */}
              </Box>
            )}

            {pathname !== "/pricing" && (
              <Box sx={{ display: { xs: "block", sm: "none" } }}>
                <IconButton
                  onClick={handleDownloadAll}
                  disabled={processedImages.length === 0}
                  sx={{
                    bgcolor:
                      processedImages.length === 0
                        ? "#FFFFFF"
                        : "rgba(139, 92, 246, 1)",
                    color: processedImages.length === 0 ? "#9CA3AF" : "#111827",
                    "&:hover": {
                      bgcolor: "rgba(139, 92, 246, 1)",
                      filter: "brightness(0.92)",
                    },
                    width: 32,
                    height: 32,
                    borderRadius: "18px",
                    boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
                  }}
                >
                  <DownloadIcon sx={{ fontSize: 20 }} />
                </IconButton>
              </Box>
            )}

            {!user && (
              <Button
                onClick={() => router.push("/auth")}
                variant="contained"
                sx={{
                  textTransform: "none",
                  bgcolor: "rgba(139, 92, 246, 1)",
                  color: "#111827",
                  fontSize: "12.5px",
                  fontWeight: 500,
                  borderRadius: "18px",
                  boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
                  "&:hover": {
                    bgcolor: "rgba(139, 92, 246, 1)",
                    filter: "brightness(0.92)",
                    boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
                  },
                  px: 3,
                  py: 0.75,
                }}
              >
                Sign In
              </Button>
            )}

            {user && (
              <Box sx={{ flexGrow: 0 }}>
                <Tooltip title="User Account">
                  <IconButton
                    onClick={handleOpenUserMenu}
                    sx={{
                      p: 0,
                      display: "flex",
                      gap: 1.5,
                      alignItems: "center",
                    }}
                  >
                    <Box
                      sx={{
                        display: { xs: "none", lg: "block" },
                        textAlign: "right",
                        mr: 1,
                      }}
                    >
                      <Typography
                        sx={{
                          fontSize: "14px",
                          fontWeight: 500,
                          color: "#111827",
                          lineHeight: 2,
                        }}
                      >
                        {user.fullName || "User"}
                      </Typography>
                      <Typography
                        sx={{
                          fontSize: 11,
                          color: "#6B7280",
                          lineHeight: 1.2,
                        }}
                      >
                        {pathname === "/dashboard" ? "Dashboard" : pathname.replace("/", "") || "Workspace"}
                      </Typography>
                    </Box>
                    <Avatar
                      alt={user.fullName}
                      src={user.avatar}
                      sx={{
                        width: { xs: 38, md: 42 },
                        height: { xs: 38, md: 42 },
                        borderRadius: "18px",
                        border: "1px solid rgba(139, 92, 246, 0.4)",
                        boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
                        transition: "all 0.2s ease",
                        "&:hover": {
                          borderColor: "#8B5CF6",
                        },
                      }}
                    >
                      {user.fullName?.charAt(0) || "U"}
                    </Avatar>
                  </IconButton>
                </Tooltip>
                <Menu
                  sx={{ mt: "45px" }}
                  id="menu-appbar"
                  anchorEl={anchorEl}
                  anchorOrigin={{
                    vertical: "top",
                    horizontal: "right",
                  }}
                  keepMounted
                  open={Boolean(anchorEl)}
                  onClose={handleCloseUserMenu}
                  PaperProps={{
                    sx: {
                      borderRadius: "18px",
                      boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
                      border: "1px solid #E5E7EB",
                      bgcolor: "#FFFFFF",
                      minWidth: "200px",
                      p: 1,
                    },
                  }}
                >
                  <Box
                    sx={{
                      px: 2,
                      py: 1.5,
                      borderBottom: "1px solid #FFFFFF",
                      mb: 1,
                    }}
                  >
                    <Typography
                      variant="subtitle2"
                      sx={{ fontWeight: 500, color: "#111827" }}
                    >
                      {user.fullName}
                    </Typography>
                    <Typography variant="caption" sx={{ color: "#6B7280" }}>
                      {user.email}
                    </Typography>
                  </Box>
                  <MenuItem
                    onClick={() => {
                      handleCloseUserMenu();
                      router.push("/dashboard");
                    }}
                  >
                    <PersonIcon
                      sx={{ mr: 1.5, fontSize: 20, color: "#6B7280" }}
                    />
                    <Typography textAlign="center">Home</Typography>
                  </MenuItem>
                  <MenuItem
                    onClick={() => {
                      handleCloseUserMenu();
                      router.push("/billing");
                    }}
                  >
                    <CreditCardIcon
                      sx={{ mr: 1.5, fontSize: 20, color: "#6B7280" }}
                    />
                    <Typography textAlign="center">Billing</Typography>
                  </MenuItem>
                  <MenuItem
                    onClick={() => {
                      handleCloseUserMenu();
                      router.push("/archive");
                    }}
                  >
                    <PhotoLibraryIcon
                      sx={{ mr: 1.5, fontSize: 20, color: "#6B7280" }}
                    />
                    <Typography textAlign="center">Archive</Typography>
                  </MenuItem>
                  <MenuItem onClick={handleLogout} sx={{ color: "#EF4444" }}>
                    <LogoutIcon sx={{ mr: 1.5, fontSize: 20 }} />
                    <Typography textAlign="center">Logout</Typography>
                  </MenuItem>
                </Menu>
              </Box>
            )}
          </Box>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
