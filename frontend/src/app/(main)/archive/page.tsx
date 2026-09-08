"use client";

import React, { useEffect, useState } from "react";
import {
  Box,
  Container,
  Typography,
  Card,
  CardMedia,
  CardContent,
  IconButton,
  Tooltip,
  Modal,
  CircularProgress,
  Button,
  Chip,
  Paper,
} from "@mui/material";
import Grid from "@mui/material/Grid";
import {
  Download as DownloadIcon,
  Fullscreen as FullscreenIcon,
  Close as CloseIcon,
} from "@mui/icons-material";
import { useRouter } from "next/navigation";
import { usePageHeader } from "@/app/context/PageHeaderContext";
import { CREAM, INK, ACCENT, TEXT_MUTED_L, BORDER_L, MONO } from "@/app/theme/terminal";
import { FadeIn, hoverCard } from "@/components/motion/Reveal";
import { motion } from "motion/react";

interface HistoryItem {
  id: string;
  url: string;
  prompt: string;
  aspectRatio: string;
  targetDims: [number, number] | null;
  timestamp: string;
  operation: string;
}

/** Map internal operation codes to user-friendly labels and icons */
const getOperationDisplay = (item: HistoryItem): { label: string; color: string; bgColor: string } => {
    let operation = item.operation;
    
    if (operation === 'resize') {
        if (item.prompt) {
            return { label: 'Generated', color: '#7c3aed', bgColor: '#f3e8ff' };
        }
        return { label: 'Transformed', color: '#059669', bgColor: '#d1fae5' };
    }

    switch (operation) {
        case 'prompt_gen':
            return { label: 'Generated', color: '#7c3aed', bgColor: '#f3e8ff' };
        case 'edit_gen':
            return { label: 'Edited', color: '#0891b2', bgColor: '#e0f7fa' };
        case 'resize_gen':
        case 'custom_resize':
        case 'resize_canvas':
            return { label: 'Transformed', color: '#059669', bgColor: '#d1fae5' };
        case 'glenn_resize':
            return { label: 'Smart Resize', color: '#d97706', bgColor: '#fef3c7' };
        default:
            return { label: 'Created', color: '#6B7280', bgColor: '#FFFFFF' };
    }
};

export default function ArchivePage() {
  const router = useRouter();
  const { setHeader, resetHeader } = usePageHeader();
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedImage, setSelectedImage] = useState<HistoryItem | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    setHeader({ title: "Archive" });
    return () => resetHeader();
  }, [setHeader, resetHeader]);

  useEffect(() => {
    const fetchHistory = async () => {
      const token = localStorage.getItem("auth_token");
      if (!token) {
        router.push("/auth");
        return;
      }

      try {
        const API_BASE_URL =
          process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";
        const response = await fetch(`${API_BASE_URL}/history`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          setHistory(data.history || []);
        }
      } catch (error) {
        console.error("Error fetching history:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [router]);

  const handleDownload = async (url: string, filename: string) => {
    try {
        const response = await fetch(url);
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = downloadUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
        console.error("Error downloading image:", error);
    }
  };

  const openFullscreen = (item: HistoryItem) => {
    setSelectedImage(item);
    setModalOpen(true);
  };

  const formatTimestamp = (dateStr: string) => {
    try {
      const date = new Date(dateStr);
      return (
        date.toLocaleDateString() +
        " " +
        date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      );
    } catch {
      return dateStr;
    }
  };

  return (
    <Box>
      <Container maxWidth="lg" sx={{ py: { xs: 2, md: 3 } }}>
        {loading ? (
          <Box sx={{ display: "flex", justifyContent: "center", py: 8 }}>
            <CircularProgress
              size={40}
              sx={{ color: ACCENT }}
            />
          </Box>
        ) : history.length === 0 ? (
          <Paper
            sx={{
              p: 6,
              textAlign: "center",
              borderRadius: "18px",
              border: `1px solid ${BORDER_L}`,
              bgcolor: "transparent",
              boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
            }}
          >
            <Typography sx={{ color: TEXT_MUTED_L, mb: 2, fontSize: "0.95rem" }}>
              You haven&apos;t generated any images yet.
            </Typography>
            <Button
              variant="contained"
              onClick={() => router.push("/dashboard")}
              sx={{
                bgcolor: ACCENT,
                color: INK,
                borderRadius: "18px",
                textTransform: "none",
                px: 3,
                boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
                fontWeight: 600,
                "&:hover": { bgcolor: ACCENT, filter: "brightness(0.94)", boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)" },
              }}
            >
              Start Generating
            </Button>
          </Paper>
        ) : (
          <Grid container spacing={2}>
            {history.map((item, i) => {
              const opDisplay = getOperationDisplay(item);
              return (
              <Grid key={item.id} size={{ xs: 12, sm: 6, md: 4, lg: 3 }}>
                <FadeIn delay={Math.min(i, 8) * 0.03} style={{ height: "100%" }}>
                <motion.div {...hoverCard} style={{ height: "100%" }}>
                <Card
                  sx={{
                    borderRadius: "18px",
                    border: `1px solid ${BORDER_L}`,
                    overflow: "hidden",
                    boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
                    transition: "border-color 0.18s",
                    "&:hover": {
                      boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
                      borderColor: ACCENT,
                    },
                    height: "100%",
                    display: "flex",
                    flexDirection: "column",
                  }}
                >
                  <Box
                    sx={{
                      position: "relative",
                      width: "100%",
                      overflow: "hidden",
                      bgcolor: "#F3F4F6",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      aspectRatio: "4 / 3",
                      height: "auto",
                    }}
                  >
                    <CardMedia
                      component="img"
                      image={item.url}
                      alt="Generated content"
                      sx={{
                        width: "100%",
                        height: "100%",
                        objectFit: "cover",
                      }}
                    />
                    <Box
                      sx={{
                        position: "absolute",
                        bottom: 0,
                        left: 0,
                        right: 0,
                        p: 1,
                        background:
                          "linear-gradient(to top, rgba(0,0,0,0.6), transparent)",
                        display: "flex",
                        justifyContent: "flex-end",
                        gap: 0.5,
                      }}
                    >
                      <Tooltip title="Fullscreen">
                        <IconButton
                          size="small"
                          onClick={() => openFullscreen(item)}
                          sx={{
                            color: "white",
                            bgcolor: "rgba(255,255,255,0.15)",
                            p: 0.5,
                            "&:hover": { bgcolor: "rgba(255,255,255,0.25)" },
                          }}
                        >
                          <FullscreenIcon sx={{ fontSize: 18 }} />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Download">
                        <IconButton
                          size="small"
                          onClick={() =>
                            handleDownload(item.url, `archive_${item.id}.png`)
                          }
                          sx={{
                            color: "white",
                            bgcolor: "rgba(255,255,255,0.15)",
                            p: 0.5,
                            "&:hover": { bgcolor: "rgba(255,255,255,0.25)" },
                          }}
                        >
                          <DownloadIcon sx={{ fontSize: 18 }} />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </Box>
                  <CardContent
                    sx={{
                      p: 0.75,
                      flexGrow: 1,
                      display: "flex",
                      flexDirection: "column",
                      justifyContent: "space-between",
                    }}
                  >
                    <Box
                      sx={{
                        display: "flex",
                        gap: 0.3,
                        flexWrap: "wrap",
                        alignItems: "center",
                      }}
                    >
                      <Chip
                          label={opDisplay.label}
                          size="small"
                          sx={{ bgcolor: opDisplay.bgColor, color: opDisplay.color, fontSize: '9px', fontWeight: 600, height: 18 }}
                      />
                      {item.prompt && (
                          <Chip
                              label="Prompted"
                              size="small"
                              sx={{ bgcolor: '#ede9fe', color: '#8b5cf6', fontSize: '9px', fontWeight: 600, height: 18 }}
                          />
                      )}
                      <Chip
                        label={item.aspectRatio}
                        size="small"
                        sx={{
                          bgcolor: "#FFFFFF",
                          color: "#4b5563",
                          fontSize: "9px",
                          fontWeight: 500,
                          height: 18,
                        }}
                      />
                      {item.targetDims && (
                        <Chip
                          label={`${item.targetDims[0]}×${item.targetDims[1]}`}
                          size="small"
                          sx={{
                            bgcolor: "#FFFFFF",
                            color: "#4b5563",
                            fontSize: "9px",
                            fontWeight: 500,
                            height: 18,
                          }}
                        />
                      )}
                    </Box>
                    <Typography
                        variant="caption"
                        sx={{
                            color: '#9CA3AF',
                            fontSize: '10px',
                            mt: 0.5,
                            display: 'block'
                        }}
                    >
                        {formatTimestamp(item.timestamp)}
                    </Typography>
                  </CardContent>
                </Card>
                </motion.div>
                </FadeIn>
              </Grid>
              );
            })}
          </Grid>
        )}
      </Container>

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          p: { xs: 1, sm: 1.5, md: 2 },
        }}
      >
        <Box
          sx={{
            position: "relative",
            width: "100%",
            maxWidth: { xs: "95vw", md: 960 },
            outline: "none",
            display: "flex",
            flexDirection: "column",
            bgcolor: CREAM,
            borderRadius: "18px",
            border: `1px solid ${BORDER_L}`,
            overflow: "hidden",
            boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
          }}
        >
          <IconButton
            onClick={() => setModalOpen(false)}
            sx={{
              position: "absolute",
              right: { xs: 8, md: 12 },
              top: { xs: 8, md: 12 },
              color: "white",
              bgcolor: "rgba(0,0,0,0.6)",
              zIndex: 10,
              p: 0.5,
              "&:hover": { bgcolor: "rgba(0,0,0,0.8)" },
            }}
          >
            <CloseIcon sx={{ fontSize: 20 }} />
          </IconButton>

          {selectedImage && (
            <>
              {/* Image Section - fixed-height preview card */}
              <Box
                sx={{
                  flexShrink: 0,
                  height: { xs: "55vh", md: "63vh" },
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  bgcolor: "#FFFFFF",
                  p: { xs: 0.5, sm: 0.75, md: 1 },
                }}
              >
                <img
                  src={selectedImage.url}
                  alt="Generated content"
                  style={{
                    maxWidth: "100%",
                    maxHeight: "100%",
                    objectFit: "contain",
                    display: "block",
                  }}
                />
              </Box>

              {/* Info Section - Fixed Layout */}
              <Box
                sx={{
                  p: { xs: 1.5, md: 2 },
                  borderTop: "1px solid #E5E7EB",
                  bgcolor: "white",
                  display: "flex",
                  flexDirection: "column",
                  flexGrow: 1,
                }}
              >
                {selectedImage.prompt && (
                  <Box 
                    sx={{ 
                      mb: 2, 
                      maxHeight: "120px", 
                      overflowY: "auto",
                      pr: 1,
                      '&::-webkit-scrollbar': { width: '4px' },
                      '&::-webkit-scrollbar-thumb': { bgcolor: '#f1f1f1', borderRadius: '10px' }
                    }}
                  >
                    <Typography
                      variant="subtitle2"
                      sx={{
                        fontWeight: 600,
                        mb: 0.5,
                        color: "#9CA3AF",
                        fontSize: "0.65rem",
                        textTransform: "uppercase",
                      }}
                    >
                      Prompt
                    </Typography>
                    <Typography
                      sx={{
                        color: "#111827",
                        fontSize: "0.85rem",
                        lineHeight: 1.5,
                      }}
                    >
                      {selectedImage.prompt}
                    </Typography>
                  </Box>
                )}

                <Box
                  sx={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: { xs: 1.5, md: 3 },
                    alignItems: "center",
                    mt: 'auto',
                    pt: 1.5,
                    borderTop: '1px solid #f1f5f9'
                  }}
                >
                  <Box>
                    <Typography
                      variant="caption"
                      sx={{
                        color: "#9CA3AF",
                        display: "block",
                        mb: 0.25,
                        fontSize: "10px",
                        fontWeight: 600,
                        textTransform: "uppercase",
                      }}
                    >
                      Type
                    </Typography>
                    <Chip
                      label={getOperationDisplay(selectedImage).label}
                      size="small"
                      sx={{
                        bgcolor: getOperationDisplay(selectedImage).bgColor,
                        color: getOperationDisplay(selectedImage).color,
                        fontSize: "11px",
                        fontWeight: 600,
                        height: 22,
                        mr: 0.5,
                      }}
                    />
                    {selectedImage.prompt && (
                      <Chip
                        label="Prompted"
                        size="small"
                        sx={{
                          bgcolor: "#ede9fe",
                          color: "#8b5cf6",
                          fontSize: "11px",
                          fontWeight: 600,
                          height: 22,
                        }}
                      />
                    )}
                  </Box>
                  <Box>
                    <Typography
                      variant="caption"
                      sx={{
                        color: "#9CA3AF",
                        display: "block",
                        mb: 0.25,
                        fontSize: "10px",
                        fontWeight: 600,
                        textTransform: "uppercase",
                      }}
                    >
                      Dimensions
                    </Typography>
                    <Typography
                      sx={{
                        fontWeight: 500,
                        color: "#111827",
                        fontSize: "0.85rem",
                      }}
                    >
                      {selectedImage.targetDims
                        ? `${selectedImage.targetDims[0]}×${selectedImage.targetDims[1]}`
                        : selectedImage.aspectRatio}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography
                      variant="caption"
                      sx={{
                        color: "#9CA3AF",
                        display: "block",
                        mb: 0.25,
                        fontSize: "10px",
                        fontWeight: 600,
                        textTransform: "uppercase",
                      }}
                    >
                      Created
                    </Typography>
                    <Typography
                      sx={{
                        fontWeight: 500,
                        color: "#111827",
                        fontSize: "0.85rem",
                      }}
                    >
                      {formatTimestamp(selectedImage.timestamp)}
                    </Typography>
                  </Box>
                  <Box sx={{ ml: "auto", display: "flex", alignItems: "center" }}>
                    <Button
                      variant="contained"
                      startIcon={<DownloadIcon />}
                      onClick={() =>
                        handleDownload(
                          selectedImage.url,
                          `archive_${selectedImage.id}.png`
                        )
                      }
                      sx={{
                        bgcolor: "rgba(139, 92, 246, 1)",
                        borderRadius: "8px",
                        textTransform: "none",
                        px: { xs: 1.5, md: 2 },
                        py: { xs: 0.5, md: 0.75 },
                        fontSize: "0.8rem",
                        height: 32,
                      }}
                    >
                      Download
                    </Button>
                  </Box>
                </Box>
              </Box>
            </>
          )}
        </Box>
      </Modal>
    </Box>
  );
}

