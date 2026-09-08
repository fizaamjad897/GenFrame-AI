"use client";
import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  Box,
  Container,
  Typography,
  Button,
  TextField,
  Paper,
  IconButton,
  Stack,
  Modal,
  CircularProgress,
  ThemeProvider,
  createTheme,
  Switch,
  FormControlLabel,
  Tooltip,
} from "@mui/material";
import UsageDisplay from "./dashboard/UsageDisplay";
import ComplianceBadge from "./compliance/ComplianceBadge";
import { useUser } from "../context/AuthContext";
import { usePageHeader } from "../context/PageHeaderContext";
import { toast } from "react-toastify";
import { extractApiErrorMessage } from "@/lib/errorMessage";
import { decodeJwtToken } from "@/lib/jwtUtils";
import { PopIn, FadeIn, hoverCard } from "@/components/motion/Reveal";
import { motion } from "motion/react";
import {
  AutoAwesome as AutoAwesomeIcon,
  Download as DownloadIcon,
  Fullscreen as FullscreenIcon,
  Close as CloseIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  CloudUpload as CloudUploadIcon,
  WarningAmberRounded as WarningAmberIcon,
  PhotoLibrary as PhotoLibraryIcon,
  AutoAwesomeMosaic as PipelineIcon,
} from "@mui/icons-material";

interface ProcessedImage {
  id: string;
  preset: string;
  url: string;
  ratio: string;
  reportId?: string;
}

interface UploadedImageFile {
  id: string;
  file: File;
  url: string;
  name: string;
}

// Local theme removed to use global ThemeRegistry

// ── Client-side image compression to prevent 413 errors ──────────────────
const MAX_UPLOAD_SIZE_BYTES = 2 * 1024 * 1024; // 2 MB target max
const MAX_DIMENSION = 2048; // Max width/height for the compressed image

/**
 * Compress an image file client-side so it fits within MAX_UPLOAD_SIZE_BYTES.
 * Uses canvas resize + JPEG compression with adaptive quality.
 * Returns the original file if it's already small enough.
 */
async function compressImage(file: File): Promise<File> {
  // Skip if already under limit
  if (file.size <= MAX_UPLOAD_SIZE_BYTES) {
    return file;
  }

  return new Promise<File>((resolve, reject) => {
    const img = new window.Image();
    const objectUrl = URL.createObjectURL(file);

    img.onload = () => {
      URL.revokeObjectURL(objectUrl);

      // Calculate new dimensions (scale down if needed)
      let { width, height } = img;
      if (width > MAX_DIMENSION || height > MAX_DIMENSION) {
        const scale = MAX_DIMENSION / Math.max(width, height);
        width = Math.round(width * scale);
        height = Math.round(height * scale);
      }

      const canvas = document.createElement("canvas");
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext("2d");
      if (!ctx) {
        reject(new Error("Canvas context not available"));
        return;
      }
      ctx.drawImage(img, 0, 0, width, height);

      // Adaptive quality: start higher, reduce until under limit
      const tryQuality = (quality: number) => {
        canvas.toBlob(
          (blob) => {
            if (!blob) {
              reject(new Error("Canvas toBlob failed"));
              return;
            }
            if (blob.size <= MAX_UPLOAD_SIZE_BYTES || quality <= 0.3) {
              const compressedFile = new File(
                [blob],
                file.name.replace(/\.[^.]+$/, ".jpg"),
                { type: "image/jpeg" },
              );
              console.log(
                `🗜️ Compressed ${(file.size / 1024 / 1024).toFixed(1)}MB → ${(compressedFile.size / 1024 / 1024).toFixed(1)}MB (q=${quality.toFixed(1)}, ${width}×${height})`,
              );
              resolve(compressedFile);
            } else {
              // Try again at lower quality
              tryQuality(quality - 0.1);
            }
          },
          "image/jpeg",
          quality,
        );
      };

      tryQuality(0.85);
    };

    img.onerror = () => {
      URL.revokeObjectURL(objectUrl);
      // If we can't load it, return the original and let the server handle it
      resolve(file);
    };

    img.src = objectUrl;
  });
}

type PresetGroup = 'standard' | 'client' | 'ooh' | 'custom';

const STANDARD_PRESETS: { id: string; label: string; ratio: string; group: PresetGroup }[] = [
  { id: 'landscape', label: 'Landscape', ratio: '16:9', group: 'standard' },
  { id: 'story', label: 'Story/Reel', ratio: '9:16', group: 'standard' },
  { id: 'square', label: 'Square', ratio: '1:1', group: 'standard' },
  { id: 'portrait', label: 'Portrait', ratio: '3:4', group: 'standard' },
  { id: 'ultrawide', label: 'Ultrawide', ratio: '21:9', group: 'standard' },
];

const OOH_MEDIA_PRESETS: { id: string; label: string; ratio: string; group: PresetGroup }[] = [
  { id: 'ooh_792x216',  label: 'OOH 792×216',   ratio: 'OOH_792x216',  group: 'ooh' },
  { id: 'ooh_800x400',  label: 'OOH 800×400',   ratio: 'OOH_800x400',  group: 'ooh' },
  { id: 'ooh_840x360',  label: 'OOH 840×360',   ratio: 'OOH_840x360',  group: 'ooh' },
  { id: 'ooh_960x576',  label: 'OOH 960×576',   ratio: 'OOH_960x576',  group: 'ooh' },
  { id: 'ooh_1024x320', label: 'OOH 1024×320',  ratio: 'OOH_1024x320', group: 'ooh' },
  { id: 'ooh_1060x360', label: 'OOH 1060×360',  ratio: 'OOH_1060x360', group: 'ooh' },
  { id: 'ooh_1232x672', label: 'OOH 1232×672',  ratio: 'OOH_1232x672', group: 'ooh' },
  { id: 'ooh_1280x384', label: 'OOH 1280×384',  ratio: 'OOH_1280x384', group: 'ooh' },
  { id: 'ooh_1344x432', label: 'OOH 1344×432',  ratio: 'OOH_1344x432', group: 'ooh' },
  { id: 'ooh_1836x432', label: 'OOH 1836×432',  ratio: 'OOH_1836x432', group: 'ooh' },
  { id: 'ooh_1952x896', label: 'OOH 1952×896',  ratio: 'OOH_1952x896', group: 'ooh' },
  { id: 'ooh_2072x252', label: 'OOH 2072×252',  ratio: 'OOH_2072x252', group: 'ooh' },
  { id: 'ooh_3924x972', label: 'OOH 3924×972',  ratio: 'OOH_3924x972', group: 'ooh' },
  { id: 'ooh_504x1008', label: 'OOH 504×1008',  ratio: 'OOH_504x1008', group: 'ooh' },
  { id: 'ooh_768x1152', label: 'OOH 768×1152',  ratio: 'OOH_768x1152', group: 'ooh' },
];

// These 6 OOH dimensions route through SignageX's own public OOH transformation
// API (transformation.signagexai.com) instead of our Gemini pipeline.
const SIGNAGEX_OOH_DIMENSIONS = new Set([
  "OOH_792X216",
  "OOH_1060X360",
  "OOH_1232X672",
  "OOH_1836X432",
  "OOH_1952X896",
  "OOH_1024X320",
]);

// Parses a ratio string ("16:9", "OOH_792x216", ...) into [w, h] for the chip glyph.
function parseRatioDims(ratio: string): [number, number] {
  const cleaned = ratio.replace(/^OOH_/, "");
  const sep = cleaned.includes(":") ? ":" : "x";
  const parts = cleaned.split(sep).map(Number);
  if (parts.length === 2 && parts.every((n) => Number.isFinite(n) && n > 0)) {
    return [parts[0], parts[1]];
  }
  return [1, 1];
}

function RatioGlyph({ ratio, color }: { ratio: string; color: string }) {
  const [rw, rh] = parseRatioDims(ratio);
  const maxDim = 24;
  const minDim = 9;
  const w = rw >= rh ? maxDim : Math.max(minDim, Math.round(maxDim * (rw / rh)));
  const h = rh >= rw ? maxDim : Math.max(minDim, Math.round(maxDim * (rh / rw)));
  return (
    <Box sx={{ width: 32, height: 32, flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <Box
        sx={{
          width: w,
          height: h,
          borderRadius: "18px",
          border: `1.5px solid ${color}`,
          bgcolor: `${color}1f`,
          transition: "all 0.18s ease",
        }}
      />
    </Box>
  );
}

/** Small L-shaped corner registration marks, like a printer's crop marks —
 * the recurring motif tying the preset picker and output array together as
 * one "production plate" visual language. */
function RegistrationTicks({ color = "rgba(17, 24, 39, 0.28)", size = 7 }: { color?: string; size?: number }) {
  const corner = (top?: number, right?: number, bottom?: number, left?: number, borders?: string) => ({
    position: "absolute" as const,
    top, right, bottom, left,
    width: size,
    height: size,
    borderColor: color,
    ...(borders === "tl" && { borderTop: `1.5px solid ${color}`, borderLeft: `1.5px solid ${color}` }),
    ...(borders === "tr" && { borderTop: `1.5px solid ${color}`, borderRight: `1.5px solid ${color}` }),
    ...(borders === "bl" && { borderBottom: `1.5px solid ${color}`, borderLeft: `1.5px solid ${color}` }),
    ...(borders === "br" && { borderBottom: `1.5px solid ${color}`, borderRight: `1.5px solid ${color}` }),
    pointerEvents: "none" as const,
  });
  return (
    <>
      <Box sx={corner(6, undefined, undefined, 6, "tl")} />
      <Box sx={corner(6, 6, undefined, undefined, "tr")} />
      <Box sx={corner(undefined, undefined, 6, 6, "bl")} />
      <Box sx={corner(undefined, 6, 6, undefined, "br")} />
    </>
  );
}

/** Monospace, tabular-figure dimension readout — used everywhere an exact
 * pixel/ratio spec is shown, so measurements read as data, not decoration. */
function SpecReadout({ children, color = "#111827", size = 12 }: { children: React.ReactNode; color?: string; size?: number }) {
  return (
    <Box
      component="span"
      sx={{
        fontFamily: "'JetBrains Mono', ui-monospace, monospace",
        fontVariantNumeric: "tabular-nums",
        fontSize: size,
        color,
        letterSpacing: "-0.01em",
      }}
    >
      {children}
    </Box>
  );
}

/** One plate in the output array — pending (ghost outline + spec), processing
 * (same outline, active pulse), or done (thumbnail + actions). The array
 * renders one of these per selected format the instant it's picked, so the
 * "one source, many exact outputs" mechanism is visible before you even hit
 * Generate, and each plate flips to done independently as it completes. */
function OutputPlate({
  label,
  ratio,
  status,
  image,
  onOpen,
  onDownload,
}: {
  label: string;
  ratio: string;
  status: "pending" | "processing" | "done";
  image: ProcessedImage | null;
  onOpen: () => void;
  onDownload: () => void;
}) {
  const displayRatio = ratio.replace(/^OOH_/, "").replace("x", "×");
  if (status === "done" && image) {
    return (
      <motion.div {...hoverCard} style={{ height: "100%" }}>
        <Paper
          elevation={0}
          sx={{
            position: "relative",
            border: "1px solid rgba(17, 24, 39, 0.14)",
            borderRadius: "10px",
            overflow: "hidden",
            height: "100%",
            display: "flex",
            flexDirection: "column",
          }}
        >
          <Box
            component="img"
            src={image.url}
            alt={label}
            onClick={onOpen}
            sx={{
              width: "100%",
              aspectRatio: "4 / 3",
              objectFit: "cover",
              cursor: "pointer",
              display: "block",
            }}
          />
          <Box sx={{ px: 1.25, py: 1, display: "flex", alignItems: "center", justifyContent: "space-between", borderTop: "1px solid rgba(17, 24, 39, 0.1)" }}>
            <Box sx={{ minWidth: 0 }}>
              <Typography sx={{ fontSize: "11px", fontWeight: 500, color: "#111827", textTransform: "uppercase", letterSpacing: "0.03em", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {label}
              </Typography>
              <SpecReadout size={11} color="#6B7280">{displayRatio}</SpecReadout>
            </Box>
            <Box sx={{ display: "flex", gap: 0.25, alignItems: "center", flexShrink: 0 }}>
              <ComplianceBadge reportId={image.reportId} />
              <IconButton size="small" onClick={onOpen} sx={{ p: 0.5, "&:hover": { bgcolor: "#E5E7EB" } }}>
                <FullscreenIcon sx={{ fontSize: 15, color: "#6B7280" }} />
              </IconButton>
              <IconButton size="small" onClick={onDownload} sx={{ p: 0.5, "&:hover": { bgcolor: "#E5E7EB" } }}>
                <DownloadIcon sx={{ fontSize: 15, color: "#6B7280" }} />
              </IconButton>
            </Box>
          </Box>
          <Box sx={{ position: "absolute", top: 6, left: 6, width: 6, height: 6, borderRadius: "50%", bgcolor: "#10B981" }} />
        </Paper>
      </motion.div>
    );
  }

  return (
    <Box
      sx={{
        position: "relative",
        border: `1px dashed ${status === "processing" ? "rgba(139, 92, 246, 0.5)" : "rgba(17, 24, 39, 0.18)"}`,
        borderRadius: "10px",
        height: "100%",
        minHeight: 132,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 0.75,
        bgcolor: status === "processing" ? "rgba(139, 92, 246, 0.03)" : "transparent",
      }}
    >
      <RegistrationTicks color={status === "processing" ? "rgba(139, 92, 246, 0.4)" : "rgba(17, 24, 39, 0.16)"} />
      {status === "processing" ? (
        <CircularProgress size={18} thickness={5} sx={{ color: "rgba(139, 92, 246, 0.8)" }} />
      ) : (
        <Box sx={{ width: 18, height: 18, border: "1.5px dashed rgba(17, 24, 39, 0.25)", borderRadius: "3px" }} />
      )}
      <Box sx={{ textAlign: "center" }}>
        <Typography sx={{ fontSize: "10.5px", fontWeight: 500, color: status === "processing" ? "rgba(139, 92, 246, 0.9)" : "#9CA3AF", textTransform: "uppercase", letterSpacing: "0.03em" }}>
          {label}
        </Typography>
        <SpecReadout size={11} color={status === "processing" ? "rgba(139, 92, 246, 0.8)" : "#9CA3AF"}>{displayRatio}</SpecReadout>
      </Box>
    </Box>
  );
}

const ImageProcessor = (props: { engineType?: string }) => {
  const engineType = props.engineType || "transformation";
  const { user, refreshUser } = useUser();
  const { setHeader } = usePageHeader();
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const promptInputRef = useRef<HTMLTextAreaElement | HTMLInputElement | null>(
    null,
  );
  const [selectedPresets, setSelectedPresets] = useState<string[]>([]);
  const [uploadedImage, setUploadedImage] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [prompt, setPrompt] = useState("");
  const [processedImages, setProcessedImages] = useState<ProcessedImage[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadedImages, setUploadedImages] = useState<UploadedImageFile[]>([]);
  const [idCounter, setIdCounter] = useState(0);
  const [selectedImage, setSelectedImage] = useState<{
    url: string;
    preset: string;
    ratio: string;
    reportId?: string;
  } | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [isLimitExceeded, setIsLimitExceeded] = useState(false);
  const [showOriginal, setShowOriginal] = useState(false);
  const [showPresetLimit, setShowPresetLimit] = useState(false);
  const [canViewCustomRatios, setCanViewCustomRatios] = useState(false);
  const [expandedOoh, setExpandedOoh] = useState(false);
  const [useJsonPipeline, setUseJsonPipeline] = useState(false);

  const presets: { id: string; label: string; ratio: string; group: PresetGroup }[] = [
    ...STANDARD_PRESETS,
    ...OOH_MEDIA_PRESETS,
  ];

  const isCustomDimPreset = (presetId: string) => {
    const preset = presets.find((p) => p.id === presetId);
    return preset?.group === "client" || preset?.group === "ooh" || preset?.group === "custom";
  };

  const parseDims = (ratio: string): { w: number; h: number } | null => {
    const parts = ratio.split(":").map(Number);
    if (parts.length === 2 && parts[0] > 0 && parts[1] > 0) {
      return { w: parts[0], h: parts[1] };
    }
    return null;
  };

  const getEngineRemainingCredits = () => {
    const engineCredits =
      (user?.engine_data?.[engineType as "transformation" | "creation"] as any)
        ?.credits || user?.credits;
    return Number(engineCredits?.remaining_units || 0);
  };

  const getEstimatedCreditsPerRequest = () => {
    const hasImage = Boolean(uploadedImage);
    const hasCustomPrompt = Boolean(prompt && prompt.trim()) && engineType === "creation";
    if (engineType === "creation" && hasImage && hasCustomPrompt) {
      return 6;
    }
    return 4;
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      toast.error('No image files found');
      return;
    }

    // Revoke previous URLs to prevent memory leaks
    uploadedImages.forEach(img => {
      if (img.url.startsWith('blob:')) {
        URL.revokeObjectURL(img.url);
      }
    });

    const newId = idCounter + 1;
    setIdCounter(newId);

    const newImage: UploadedImageFile = {
      id: `img-${newId}`,
      file,
      url: URL.createObjectURL(file),
      name: file.name,
    };

    setUploadedImages([newImage]);
    setUploadedImage(newImage.file);
    setPreviewUrl(newImage.url);
    setProcessedImages([]);

    // Reset file input so user can re-upload the same file
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleImageSelect = (image: UploadedImageFile) => {
    setUploadedImage(image.file);
    setPreviewUrl(image.url);
    setProcessedImages([]);
  };

  const MAX_PRESETS = 2;
  const handleRemoveImage = (imageId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setUploadedImages((prev) => {
      const imageToRemove = prev.find((img) => img.id === imageId);
      if (imageToRemove && imageToRemove.url.startsWith("blob:")) {
        URL.revokeObjectURL(imageToRemove.url);
      }
      return prev.filter((img) => img.id !== imageId);
    });

    // If the removed image was selected, clear the preview
    const removedImage = uploadedImages.find((img) => img.id === imageId);
    if (removedImage && previewUrl === removedImage.url) {
      setUploadedImage(null);
      setPreviewUrl("");
      setProcessedImages([]);
    }
  };

  const handlePresetChange = (presetId: string) => {
    // Deselect — always allowed
    if (selectedPresets.includes(presetId)) {
      setSelectedPresets(selectedPresets.filter((p) => p !== presetId));
      return;
    }
    // Block if at limit
    if (selectedPresets.length >= MAX_PRESETS) {
      setShowPresetLimit(true);
      return;
    }
    setSelectedPresets([...selectedPresets, presetId]);
  };

  useEffect(() => {
    const GLEN_ORG_ID = "d9f031dc-ba8f-4397-9534-81612cc8a686";
    const HAMZA_ORG_ID = "35cd976c-d4ac-4e76-8dde-d8065334fa42";

    let hasAccess = false;

    // Check 1: User object's _org_context
    const orgContext = (user as any)?._org_context || {};
    const orgId = String(orgContext.org_id || "").trim();
    const parentOrgId = String(orgContext.parent_org_id || "").trim();
    
    if (orgId === HAMZA_ORG_ID || parentOrgId === HAMZA_ORG_ID) {
      hasAccess = true;
    }
    // Only Glen's main org, NOT sub-orgs
    if (orgId === GLEN_ORG_ID) {
      hasAccess = true;
    }

    // Check 2: JWT token (fallback)
    if (!hasAccess) {
      try {
        const token = localStorage.getItem("auth_token");
        const decoded = token ? decodeJwtToken(token) : null;
        const jwtOrgId = String(decoded?.orgId || decoded?.org_id || "").trim();
        const jwtParentOrgId = String(
          decoded?.parentOrgId ||
            decoded?.org_parent_id ||
            decoded?.orgParentId ||
            "",
        ).trim();
        
        if (jwtOrgId === HAMZA_ORG_ID || jwtParentOrgId === HAMZA_ORG_ID) {
          hasAccess = true;
        }
        if (jwtOrgId === GLEN_ORG_ID) {
          hasAccess = true;
        }
      } catch {
        hasAccess = false;
      }
    }

    // Check 3: Email/domain fallback for testing
    if (!hasAccess) {
      const email = String(user?.email || "")
        .trim()
        .toLowerCase();
      const domain = email.includes("@") ? email.split("@")[1] : "";
      hasAccess =
        email === "muhammadhamzafaisal146@gmail.com" ||
        domain === "fmctv.co.nz";
    }

    setCanViewCustomRatios(hasAccess);
  }, [user]);

  useEffect(() => {
    if (!canViewCustomRatios) {
      setSelectedPresets((prev) =>
        prev.filter((id) => {
          const preset = presets.find((p) => p.id === id);
          return preset?.group !== "client" && preset?.group !== "ooh";
        }),
      );
    }
  }, [canViewCustomRatios]);

  // Helper: extract the image URL + compliance reportId from a response (handles binary and JSON)
  const extractResult = async (
    response: Response,
  ): Promise<{ url: string; reportId?: string }> => {
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.startsWith("image/")) {
      const blob = await response.blob();
      return { url: URL.createObjectURL(blob) };
    }
    try {
      const text = await response.text();
      const data = JSON.parse(text);
      return {
        url: data.url || data.image_url || data.data?.url || previewUrl,
        reportId: data.reportId,
      };
    } catch {
      return { url: previewUrl };
    }
  };

  const extractResponseErrorMessage = async (
    response: Response,
    fallback: string,
  ): Promise<string> => {
    try {
      const contentType = response.headers.get("content-type") || "";
      if (contentType.includes("application/json")) {
        const data = await response.json();
        return data?.detail || data?.message || data?.error || fallback;
      }

      const text = (await response.text())?.trim();
      return text || response.statusText || fallback;
    } catch {
      return response.statusText || fallback;
    }
  };

  const handleProcessImage = async () => {
    if (!user) {
      toast.error("Please login to process images");
      router.push("/auth");
      return;
    }

    // Validation
    const isImageMissing = !uploadedImage;
    const isPromptMissing = !prompt || !prompt.trim();
    const hasPresets = selectedPresets.length > 0;

    if (engineType === "transformation" && isImageMissing) {
      toast.error("Please upload an image for the Transformation engine");
      return;
    }

    if (engineType === "creation" && isImageMissing && isPromptMissing) {
      toast.error(
        "Please provide either an image or a prompt for the Creation engine",
      );
      return;
    }

    if (!hasPresets) {
      if (engineType === "creation" && prompt.trim()) {
        // Allow creation engine with prompt to default to square
      } else {
        toast.error("Please select at least one preset");
        return;
      }
    }

    const isPostpaid = Boolean((user as any).is_postpaid);
    const remainingCredits = getEngineRemainingCredits();
    const estimatedCreditsPerRequest = getEstimatedCreditsPerRequest();

    if (!isPostpaid && remainingCredits < estimatedCreditsPerRequest) {
      setIsLimitExceeded(true);
      toast.error(
        `Insufficient credits. Need ${estimatedCreditsPerRequest.toFixed(1)}, have ${remainingCredits.toFixed(1)}.`,
      );
      return;
    }

    setIsProcessing(true);
    setProcessedImages([]);
    const toastId = toast.loading(
      engineType === "transformation"
        ? "Processing transformation..."
        : "Processing creation request...",
    );

    const token = localStorage.getItem("auth_token");
    const API_BASE_URL =
      process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";

    // Compress the image once up front so every preset reuses the same blob
    let imageToUpload: File | null = null;
    if (uploadedImage) {
      try {
        imageToUpload = await compressImage(uploadedImage);
      } catch (err) {
        console.warn("Image compression failed, using original:", err);
        imageToUpload = uploadedImage;
      }
    }

    try {
      const results: ProcessedImage[] = [];
      const failedMessages: string[] = [];
      let insufficientCreditsMessage: string | null = null;

      // Helper: make a single resize request and parse the result
      const callResize = async (
        aspectRatio: string,
        label: string,
        id: string,
        useCustomEndpoint = false,
      ): Promise<ProcessedImage | null> => {
        const formData = new FormData();
        if (imageToUpload) formData.append("file", imageToUpload);
        formData.append("engine_type", engineType);
        if (prompt.trim()) formData.append("prompt", prompt);

        let endpoint = `${API_BASE_URL}/resize`;
        if (SIGNAGEX_OOH_DIMENSIONS.has(aspectRatio.toUpperCase())) {
          formData.append("dimension", aspectRatio.toUpperCase());
          endpoint = `${API_BASE_URL}/ooh/resize`;
        } else if (useCustomEndpoint) {
          const dimMatch = aspectRatio.match(/^(\d+)[x:](\d+)$/i);
          if (!dimMatch) {
            throw new Error("Invalid custom dimensions format");
          }
          formData.append("width", dimMatch[1]);
          formData.append("height", dimMatch[2]);
          endpoint = `${API_BASE_URL}/custom-resize`;
        } else {
          formData.append("aspect_ratio", aspectRatio);
          if (useJsonPipeline) formData.append("use_json_pipeline", "true");
        }

        const response = await fetch(endpoint, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
          body: formData,
        });

        if (!response.ok) {
          // Surface the real error to the user for known status codes
          if (response.status === 413) {
            throw new Error(
              `Image is too large for ${label}. Please use a smaller image (under 2 MB).`,
            );
          }
          const errText = await extractResponseErrorMessage(
            response,
            `Failed to process ${label}`,
          );
          if (response.status === 429) {
            throw new Error(errText);
          }
          console.error(`Failed to process ${label}: ${response.status} ${errText}`);
          return null;
        }

        const { url: imageUrl, reportId } = await extractResult(response);
        return { id, preset: label, url: imageUrl, ratio: aspectRatio, reportId };
      };

      // Process selected presets
      const presetsToProcess = hasPresets
        ? selectedPresets
        : engineType === "creation" && prompt.trim()
          ? ["square"]
          : [];

      const failedLabels: string[] = [];

      const presetPromises = presetsToProcess.map(async (presetId, index) => {
        const preset = presets.find((p) => p.id === presetId);
        if (!preset) return;

        try {
          const dims = parseDims(preset.ratio);
          const useCustomEndpoint =
            canViewCustomRatios && isCustomDimPreset(preset.id) && !!dims;

          const result = await callResize(
            preset.ratio,
            preset.label,
            `res-${Date.now()}-${preset.id}-${index}`,
            useCustomEndpoint,
          );
          if (result) {
            results.push(result);
            // Surface each plate the moment it completes, rather than waiting
            // for every preset to finish — the output array fills in live.
            setProcessedImages((prev) => [...prev, result]);
          } else {
            failedLabels.push(preset.label);
          }
        } catch (e) {
          const message = extractApiErrorMessage(e, `Failed to process ${preset.label}`);
          if (/insufficient credits/i.test(message)) {
            insufficientCreditsMessage = message;
          }
          failedLabels.push(preset.label);
        }
      });

      await Promise.all(presetPromises);

      setProcessedImages(results);

      const totalExpected = presetsToProcess.length;

      if (results.length === totalExpected && results.length > 0) {
        toast.update(toastId, {
          render: `Successfully generated ${results.length} images!`,
          type: "success",
          isLoading: false,
          autoClose: 3000,
        });
      } else if (results.length > 0) {
        toast.update(toastId, {
          render: `Partial success: Generated ${results.length} images, but failed on: ${failedLabels.join(", ")}`,
          type: "warning",
          isLoading: false,
          autoClose: 5000,
        });
      } else {
        if (insufficientCreditsMessage) {
          setIsLimitExceeded(true);
        }
        toast.update(toastId, {
          render:
            insufficientCreditsMessage ||
            `Failed to process image(s). Ensure you have enough credits or try again.`,
          type: "error",
          isLoading: false,
          autoClose: 5000,
        });
      }
    } catch (error: any) {
      console.error("Error processing image:", error);
      toast.update(toastId, {
        render: extractApiErrorMessage(error, "Failed to process image"),
        type: "error",
        isLoading: false,
        autoClose: 5000,
      });
    } finally {
      setIsProcessing(false);
      refreshUser();
    }
  };

  const handleOpenModal = (image: {
    url: string;
    preset: string;
    ratio: string;
    reportId?: string;
  }) => {
    setSelectedImage(image);
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setSelectedImage(null);
  };

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
      toast.error(extractApiErrorMessage(error, "Failed to download image"));
    }
  };

  const handleDownloadAll = async () => {
    if (processedImages.length === 0) return;
    for (const image of processedImages) {
      await handleDownload(image.url, `${image.preset}-${image.ratio}.png`);
      // Add a slight delay between downloads to prevent browser throttling
      await new Promise((resolve) => setTimeout(resolve, 300));
    }
  };

  // useEffect(() => {
  //   setHeader({
  //     actionLabel: "Download Output",
  //     actionDisabled: processedImages.length === 0,
  //     onAction: handleDownloadAll,
  //   });

  //   return () => {
  //     setHeader({
  //       actionLabel: undefined,
  //       actionDisabled: undefined,
  //       onAction: undefined,
  //     });
  //   };
  // }, [processedImages, setHeader]);

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "#FFFFFF" }}>
      {/* Description Section */}
      <Box
        sx={{
          position: "relative",
          bgcolor: "#FFFFFF",
          // borderBottom: '1px solid #E5E7EB',
          py: { xs: 1.5, md: 2 },
          // px: { xs: 1.5, sm: 2, md: 3, lg: 3 },
          overflow: "hidden",
        }}
      >
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            overflow: 'hidden',
            zIndex: 0,
          }}
        >
          <video
            autoPlay
            muted
            loop
            playsInline
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              opacity: '0.08',
            }}
          >
            <source src="/bg-video-new.mp4" type="video/mp4" />
          </video>
        </Box>
        <Container
          maxWidth={false}
          sx={{
            px: 0,
            position: "relative",
            zIndex: 1,
          }}
        >
          <Box
            sx={{
              maxWidth: "1200px",
              mx: "auto",
              display: "flex",
              flexDirection: "column",
              gap: 3,
            }}
          >
            {/* 
            <Box sx={{ flex: 1, textAlign: { xs: 'center', md: 'left' }, pt: { xs: 2, md: 4 } }}>
              <Typography
                variant="h4"
                sx={{
                  fontSize: { xs: '32px', md: '42px', lg: '48px' },
                  fontWeight: 500,
                  color: '#111827',
                  mb: 2.5,
                  letterSpacing: '-0.02em',
                  lineHeight: 1.1,
                }}
              >
                Neural <br />
                <Box
                  component="span"
                  sx={{
                    color: 'rgba(139, 92, 246, 1)',
                  }}
                >
                  {engineType === 'transformation' ? 'Transformation Engine' : 'Creation Engine'}
                </Box>
              </Typography>
              <Typography
                sx={{
                  fontSize: '15px',
                  color: '#4b5563',
                  lineHeight: 1.6,
                  maxWidth: '600px',
                  mx: { xs: 'auto', md: 0 },
                  fontWeight: 450,
                }}
              >
                Provision, resize, and optimize high-density content in sub-seconds.
                The intelligent infrastructure layer for automated visual batch operations.
              </Typography>
            </Box>
            */}
            {/* Job Ticket — a single technical readout bar replaces the old
                icon+label feature-card grid; ticks mark each field like a
                punched production ticket instead of separate dashboard cards. */}
            <PopIn style={{ width: "100%" }}>
            <Box
              sx={{
                position: "relative",
                display: "flex",
                flexWrap: "wrap",
                alignItems: "stretch",
                border: "1px solid rgba(17, 24, 39, 0.16)",
                borderRadius: "10px",
                bgcolor: "#FFFFFF",
                width: "100%",
                maxWidth: "1200px",
                mx: "auto",
                overflow: "hidden",
              }}
            >
              <RegistrationTicks color="rgba(139, 92, 246, 0.35)" />
              {[
                { label: "Engine", value: engineType === "transformation" ? "Transformation" : "Creation" },
                { label: "Format Library", value: "47+ specs" },
                { label: "Throughput", value: "~10–30s / plate" },
              ].map((field, idx) => (
                <Box
                  key={field.label}
                  sx={{
                    px: 2.25,
                    py: 1.5,
                    borderRight: { xs: "none", sm: "1px dashed rgba(17, 24, 39, 0.14)" },
                    borderBottom: { xs: idx < 2 ? "1px dashed rgba(17, 24, 39, 0.14)" : "none", sm: "none" },
                    flex: { xs: "1 1 50%", sm: "0 0 auto" },
                  }}
                >
                  <Typography sx={{ fontSize: "9.5px", fontWeight: 500, color: "rgba(139, 92, 246, 0.7)", textTransform: "uppercase", letterSpacing: "0.06em", mb: 0.3 }}>
                    {field.label}
                  </Typography>
                  <SpecReadout size={13} color="#111827">{field.value}</SpecReadout>
                </Box>
              ))}
              <Box sx={{ ml: "auto", display: "flex", alignItems: "center", borderLeft: "1px dashed rgba(17, 24, 39, 0.14)", pl: 2.25, py: 0.75 }}>
                <UsageDisplay horizontal engineType={engineType as any} />
              </Box>
            </Box>
            </PopIn>
          </Box>
        </Container>
      </Box>

      <Container
        maxWidth={false}
        sx={{
          py: { xs: 2, md: 3 },
          px: { xs: 1.5, sm: 2, md: 3, lg: 3 },
          width: "100%",
          maxWidth: "100%",
        }}
      >
        {/* Subheader: Credit Usage */}
        {/* <UsageDisplay horizontal engineType={engineType as any} /> */}

        {/* Main Grid - 3 Columns */}
        <Box
          sx={{
            display: "flex",
            gap: { xs: 2, lg: 3 },
            flexDirection: { xs: "column", lg: "row" },
            alignItems: "flex-start",
          }}
        >
          {/* Column 1 - Prompt + Upload/Presets (with sub-columns) + Button */}
          <Box
            sx={{
              width: { xs: "100%", lg: "calc(50% - 12px)" },
              flexShrink: 0,
              display: "flex",
              flexDirection: "column",
              gap: 2,
            }}
          >
            {/* Sub-columns container (row-wise) */}
            <Box
              sx={{
                display: "flex",
                flexDirection: "row",
                gap: 2,
                width: "100%",
                flexWrap: "wrap",
              }}
            >
              {/* Sub-column 1: Prompt Section - Show ONLY if Creation Engine */}
              {engineType === "creation" && (
                <Box sx={{ flex: "1 1 48%", minWidth: "250px" }}>
                  <Typography
                    sx={{
                      fontSize: "15px",
                      fontWeight: 500,
                      color: "#111827",
                      mb: 1.5,
                    }}
                  >
                    Neural Prompt
                  </Typography>
                  <Paper
                    elevation={0}
                    onClick={() => promptInputRef.current?.focus()}
                    sx={{
                      border: "1px solid rgba(17, 24, 39, 0.16)",
                      borderRadius: "18px",
                      overflow: "hidden",
                      display: "flex",
                      flexDirection: "column",
                      height: "300px",
                      cursor: "text",
                      bgcolor: "white",
                      boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
                    }}
                  >
                    <Box
                      sx={{
                        flex: 1,
                        p: { xs: 2, md: 3 },
                        position: "relative",
                        bgcolor: "white",
                      }}
                    >
                      {!prompt && (
                        <Box
                          sx={{
                            position: "absolute",
                            top: 24,
                            left: 24,
                            pointerEvents: "none",
                            zIndex: 1,
                          }}
                        >
                          <Typography
                            sx={{
                              fontSize: "14px",
                              color: "#9CA3AF",
                              mb: 0.5,
                              lineHeight: 1.5,
                            }}
                          >
                            Describe your enhancement...
                          </Typography>
                          <Typography
                            sx={{
                              fontSize: "14px",
                              color: "#9CA3AF",
                              lineHeight: 1.5,
                            }}
                          >
                            e.g. &apos;Make this look like a vintage
                            photograph&apos;
                          </Typography>
                        </Box>
                      )}
                      <TextField
                        multiline
                        fullWidth
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        inputRef={promptInputRef}
                        variant="standard"
                        InputProps={{
                          disableUnderline: true,
                        }}
                        sx={{
                          "& .MuiInputBase-root": {
                            height: "100%",
                            alignItems: "flex-start",
                            p: 0,
                          },
                          "& .MuiInputBase-input": {
                            fontSize: "14px",
                            color: "#374151",
                            lineHeight: 1.6,
                            "&::placeholder": {
                              opacity: 0,
                            },
                          },
                        }}
                      />
                    </Box>

                    {/* Bottom Info */}
                    <Box
                      sx={{
                        borderTop: "1px solid #E5E7EB",
                        px: 3,
                        py: 2,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        bgcolor: "#FFFFFF",
                      }}
                    >
                      <Typography
                        sx={{
                          fontSize: "12px",
                          color: "#6B7280",
                          fontWeight: 500,
                        }}
                      >
                        Optional AI enhancement
                      </Typography>
                      <AutoAwesomeIcon
                        sx={{ fontSize: 18, color: "rgba(139, 92, 246, 0.5)" }}
                      />
                    </Box>
                  </Paper>
                </Box>
              )}

              {/* Sub-column 2: Upload & Options Section */}
              <Box
                sx={{
                  flex:
                    engineType === "transformation" ? "1 1 48%" : "1 1 100%",
                  minWidth: "250px",
                }}
              >
                <Typography
                  sx={{
                    fontSize: "15px",
                    fontWeight: 500,
                    color: "#111827",
                    mb: 1.5,
                  }}
                >
                  {engineType === "creation"
                    ? "Generative Options"
                    : "Scaling Options"}
                </Typography>
                <Box
                  sx={{
                    display: "flex",
                    flexDirection: "column",
                    maxHeight: "440px",
                    overflowY: "auto",
                    "&::-webkit-scrollbar": {
                      width: "4px",
                    },
                    "&::-webkit-scrollbar-thumb": {
                      bgcolor: "#E5E7EB",
                      borderRadius: "4px",
                    },
                  }}
                >
                  <Stack spacing={3}>
                    {/* Uploaded Images Folder View */}
                    {uploadedImages.length > 0 && (
                      <Paper
                        elevation={0}
                        sx={{
                          border: "1px solid rgba(17, 24, 39, 0.16)",
                          borderRadius: "18px",
                          p: 2,
                          boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
                        }}
                      >
                        <Typography
                          sx={{
                            fontSize: "14px",
                            fontWeight: 500,
                            color: "#111827",
                            mb: 2,
                          }}
                        >
                          Uploaded Images
                        </Typography>
                        <Box
                          sx={{
                            display: "flex",
                            flexDirection: "row",
                            overflowX: "auto",
                            gap: 2,
                            pt: 1.5,
                            pb: 1.5,
                            "&::-webkit-scrollbar": {
                              height: "6px",
                            },
                            "&::-webkit-scrollbar-track": {
                              background: "rgba(0,0,0,0.02)",
                              borderRadius: "10px",
                            },
                            "&::-webkit-scrollbar-thumb": {
                              background: "rgba(139, 92, 246, 0.15)",
                              borderRadius: "10px",
                              "&:hover": {
                                background: "rgba(139, 92, 246, 0.3)",
                              },
                            },
                          }}
                        >
                          {uploadedImages.map((img) => (
                            <Box
                              key={img.id}
                              sx={{ minWidth: "140px", flexShrink: 0 }}
                            >
                              <Paper
                                elevation={0}
                                onClick={() => handleImageSelect(img)}
                                sx={{
                                  border:
                                    previewUrl === img.url
                                      ? "1.5px solid rgba(139, 92, 246, 1)"
                                      : "1px solid #E5E7EB",
                                  borderRadius: "8px",
                                  p: 1.5,
                                  cursor: "pointer",
                                  textAlign: "center",
                                  transition: "all 0.2s ease",
                                  position: "relative",
                                  "&:hover": {
                                    bgcolor: "#FFFFFF",
                                    borderColor: "rgba(139, 92, 246, 0.4)",
                                    transform: "translateY(-2px)",
                                  },
                                }}
                              >
                                <IconButton
                                  onClick={(e) => handleRemoveImage(img.id, e)}
                                  sx={{
                                    position: "absolute",
                                    top: 4,
                                    right: 4,
                                    bgcolor: "rgba(0, 0, 0, 0.5)",
                                    color: "white",
                                    width: 24,
                                    height: 24,
                                    "&:hover": {
                                      bgcolor: "rgba(0, 0, 0, 0.7)",
                                    },
                                  }}
                                  size="small"
                                >
                                  <CloseIcon sx={{ fontSize: "16px" }} />
                                </IconButton>
                                <Box
                                  sx={{
                                    width: "100%",
                                    height: 80,
                                    mb: 1,
                                    borderRadius: "4px",
                                    overflow: "hidden",
                                    bgcolor: "#FFFFFF",
                                    display: "flex",
                                    alignItems: "center",
                                    justifyContent: "center",
                                  }}
                                >
                                  <Box
                                    component="img"
                                    src={img.url}
                                    alt={img.name}
                                    sx={{
                                      maxWidth: "100%",
                                      maxHeight: "100%",
                                      objectFit: "cover",
                                    }}
                                  />
                                </Box>
                                <Typography
                                  sx={{
                                    fontSize: "11px",
                                    color: "#6B7280",
                                    overflow: "hidden",
                                    textOverflow: "ellipsis",
                                    whiteSpace: "nowrap",
                                  }}
                                >
                                  {img.name}
                                </Typography>
                              </Paper>
                            </Box>
                          ))}
                        </Box>
                      </Paper>
                    )}

                    {/* Upload & Presets Box */}
                    <Paper
                      elevation={0}
                      sx={{
                        border: "1px solid rgba(17, 24, 39, 0.16)",
                        borderRadius: "18px",
                        p: 2.5,
                        boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
                      }}
                    >
                      {/* Upload Area */}
                      <Box
                        component="label"
                        sx={{
                          display: "block",
                          cursor: "pointer",
                          mb: 3,
                        }}
                      >
                        <input
                          ref={fileInputRef}
                          type="file"
                          accept="image/*"
                          onChange={handleImageUpload}
                          style={{ display: "none" }}
                        />
                        <motion.div whileHover={{ scale: 1.005 }} whileTap={{ scale: 0.995 }}>
                        <Box
                          sx={{
                            border: "2px dashed rgba(139, 92, 246, 0.25)",
                            borderRadius: "18px",
                            py: 5,
                            textAlign: "center",
                            transition: "all 0.2s ease",
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                            gap: 1,
                            "&:hover": {
                              borderColor: "rgba(139, 92, 246, 0.55)",
                              bgcolor: "rgba(139, 92, 246, 0.04)",
                            },
                          }}
                        >
                          <Box
                            sx={{
                              width: 44,
                              height: 44,
                              borderRadius: "18px",
                              border: "1px solid rgba(139, 92, 246, 0.4)",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              color: "rgba(139, 92, 246, 1)",
                              mb: 0.5,
                            }}
                          >
                            <CloudUploadIcon sx={{ fontSize: 22 }} />
                          </Box>
                          <Typography
                            sx={{
                              fontSize: "14px",
                              fontWeight: 500,
                              color: "#374151",
                            }}
                          >
                            {engineType === "creation"
                              ? "Click to upload image (Optional)"
                              : "Click to upload image"}
                          </Typography>
                          <Typography sx={{ fontSize: "12px", color: "#9CA3AF" }}>
                            PNG, JPG or WEBP
                          </Typography>
                        </Box>
                        </motion.div>
                      </Box>

                      {/* Presets Section */}
                      <Typography
                        sx={{
                          fontSize: "14px",
                          fontWeight: 500,
                          color: "#111827",
                          mb: 1.5,
                        }}
                      >
                        Select Presets
                      </Typography>
                      <Box sx={{ mb: 3 }}>
                        <Typography
                          sx={{
                            fontSize: "11px",
                            fontWeight: 500,
                            color: "#9CA3AF",
                            textTransform: "uppercase",
                            letterSpacing: "0.05em",
                            mb: 1,
                          }}
                        >
                          Standard Ratios
                        </Typography>
                        <Box
                          sx={{
                            display: "grid",
                            gridTemplateColumns: "repeat(2, 1fr)",
                            gap: 1,
                            mb: canViewCustomRatios ? 3 : 0,
                          }}
                        >
                          {presets
                            .filter((p) => p.group === "standard")
                            .map((preset) => {
                              const selected = selectedPresets.includes(preset.id);
                              return (
                                <Paper
                                  key={preset.id}
                                  elevation={0}
                                  component="label"
                                  onClick={() => handlePresetChange(preset.id)}
                                  sx={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 1.25,
                                    px: 1.75,
                                    py: 1.5,
                                    position: "relative",
                                    border: `1px solid ${selected ? "rgba(139, 92, 246, 0.6)" : "rgba(17, 24, 39, 0.14)"}`,
                                    bgcolor: selected ? "rgba(139, 92, 246, 0.05)" : "#fff",
                                    borderRadius: "10px",
                                    cursor: "pointer",
                                    transition: "all 0.18s ease",
                                    "&:hover": {
                                      borderColor: "rgba(139, 92, 246, 0.45)",
                                    },
                                  }}
                                >
                                  <RegistrationTicks color={selected ? "rgba(139, 92, 246, 0.55)" : "rgba(17, 24, 39, 0.2)"} />
                                  <RatioGlyph ratio={preset.ratio} color="#8B5CF6" />
                                  <Box sx={{ minWidth: 0 }}>
                                    <Typography
                                      sx={{
                                        fontSize: "12px",
                                        color: selected ? "rgba(139, 92, 246, 1)" : "#6B7280",
                                        fontWeight: 500,
                                        textTransform: "uppercase",
                                        letterSpacing: "0.04em",
                                        lineHeight: 1.4,
                                      }}
                                    >
                                      {preset.label}
                                    </Typography>
                                    <SpecReadout size={14} color={selected ? "#111827" : "#374151"}>
                                      {preset.ratio}
                                    </SpecReadout>
                                  </Box>
                                  {selected && (
                                    <CheckCircleIcon
                                      sx={{
                                        position: "absolute",
                                        top: 6,
                                        right: 6,
                                        fontSize: 14,
                                        color: "rgba(139, 92, 246, 1)",
                                      }}
                                    />
                                  )}
                                </Paper>
                              );
                            })}
                        </Box>

                        {canViewCustomRatios && (
                          <>
                            {/* OOH Media Screens Section */}
                            <Box sx={{ borderTop: "1px solid #E5E7EB", my: 2.5 }} />
                            <Typography
                              sx={{
                                fontSize: "11px",
                                fontWeight: 500,
                                color: "#9CA3AF",
                                textTransform: "uppercase",
                                letterSpacing: "0.05em",
                                mb: 1.5,
                              }}
                            >
                              OOH Media
                            </Typography>

                            <Box sx={{ mb: 0.75 }}>
                              <Box
                                onClick={() => setExpandedOoh((v) => !v)}
                                sx={{
                                  display: "flex",
                                  alignItems: "center",
                                  justifyContent: "space-between",
                                  px: 1.5,
                                  py: 0.9,
                                  bgcolor: OOH_MEDIA_PRESETS.some((p) => selectedPresets.includes(p.id))
                                    ? "rgba(236,253,245,0.6)"
                                    : "#FFFFFF",
                                  border: `1px solid ${OOH_MEDIA_PRESETS.some((p) => selectedPresets.includes(p.id)) ? "rgba(16,185,129,0.3)" : "#E5E7EB"}`,
                                  borderRadius: "8px",
                                  cursor: "pointer",
                                  userSelect: "none",
                                  transition: "all 0.15s ease",
                                  "&:hover": { bgcolor: "#e6f9f2" },
                                }}
                              >
                                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                                  <Typography sx={{ fontSize: "13px", fontWeight: 500, color: "#374151" }}>
                                    OOH Media
                                  </Typography>
                                  <Typography sx={{ fontSize: "11px", color: "#9CA3AF", fontWeight: 500 }}>
                                    {OOH_MEDIA_PRESETS.length}
                                  </Typography>
                                </Box>
                                <ExpandMoreIcon
                                  sx={{
                                    fontSize: 16,
                                    color: "#9CA3AF",
                                    transform: expandedOoh ? "rotate(180deg)" : "rotate(0deg)",
                                    transition: "transform 0.2s ease",
                                  }}
                                />
                              </Box>

                              {expandedOoh && (
                                <Box
                                  sx={{
                                    display: "grid",
                                    gridTemplateColumns: "repeat(2, 1fr)",
                                    gap: 0.75,
                                    mt: 0.75,
                                    pl: 0.5,
                                  }}
                                >
                                  {OOH_MEDIA_PRESETS.map((preset) => {
                                    const selected = selectedPresets.includes(preset.id);
                                    return (
                                      <Paper
                                        key={preset.id}
                                        elevation={0}
                                        component="label"
                                        onClick={() => handlePresetChange(preset.id)}
                                        sx={{
                                          display: "flex",
                                          alignItems: "center",
                                          gap: 1,
                                          px: 1.5,
                                          py: 1.25,
                                          position: "relative",
                                          border: `1px solid ${selected ? "rgba(16,185,129,0.6)" : "rgba(17, 24, 39, 0.14)"}`,
                                          bgcolor: selected ? "rgba(16,185,129,0.06)" : "#fff",
                                          borderRadius: "10px",
                                          cursor: "pointer",
                                          transition: "all 0.15s ease",
                                          "&:hover": { borderColor: "rgba(16,185,129,0.4)" },
                                        }}
                                      >
                                        <RegistrationTicks color={selected ? "rgba(16,185,129,0.55)" : "rgba(17, 24, 39, 0.2)"} size={6} />
                                        <RatioGlyph ratio={preset.ratio} color="#10B981" />
                                        <Box sx={{ minWidth: 0 }}>
                                          <SpecReadout size={13} color={selected ? "rgba(5,150,105,1)" : "#111827"}>
                                            {preset.ratio.replace("OOH_", "").replace("x", "×")}
                                          </SpecReadout>
                                          <Typography sx={{ fontSize: "9.5px", color: "#9CA3AF", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                                            OOH · px
                                          </Typography>
                                        </Box>
                                        {selected && (
                                          <CheckCircleIcon
                                            sx={{
                                              position: "absolute",
                                              top: 5,
                                              right: 5,
                                              fontSize: 13,
                                              color: "rgba(16,185,129,1)",
                                            }}
                                          />
                                        )}
                                      </Paper>
                                    );
                                  })}
                                </Box>
                              )}
                            </Box>
                          </>
                        )}
                      </Box>
                    </Paper>
                  </Stack>
                </Box>
              </Box>
            </Box>

            {/* JSON Pipeline toggle — transformation engine only */}
            {engineType === "transformation" && (
              <Tooltip
                title="Converts the image to a structured JSON layout, mathematically resizes every element, then reconstructs the image. More precise than prompt-only resizing."
                placement="top"
                arrow
              >
                <Box
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    gap: 1.25,
                    px: 2,
                    py: 1.25,
                    borderRadius: "18px",
                    border: useJsonPipeline
                      ? "1.5px solid rgba(139, 92, 246, 0.4)"
                      : "1px solid #E5E7EB",
                    bgcolor: useJsonPipeline
                      ? "rgba(139, 92, 246, 0.05)"
                      : "#fff",
                    boxShadow: "0 2px 8px rgba(0,0,0,0.02)",
                    transition: "all 0.2s ease",
                    cursor: "pointer",
                  }}
                  onClick={() => setUseJsonPipeline((v) => !v)}
                >
                  <Box
                    sx={{
                      width: 32,
                      height: 32,
                      borderRadius: "9px",
                      flexShrink: 0,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      bgcolor: useJsonPipeline ? "rgba(139, 92, 246, 0.10)" : "#FFFFFF",
                      color: useJsonPipeline ? "rgba(139, 92, 246, 1)" : "#9CA3AF",
                      transition: "all 0.2s ease",
                    }}
                  >
                    <PipelineIcon sx={{ fontSize: 17 }} />
                  </Box>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={useJsonPipeline}
                        onChange={(e) => {
                          e.stopPropagation();
                          setUseJsonPipeline(e.target.checked);
                        }}
                        size="small"
                        sx={{
                          "& .MuiSwitch-switchBase.Mui-checked": {
                            color: "rgba(139, 92, 246, 1)",
                          },
                          "& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track":
                            {
                              bgcolor: "rgba(139, 92, 246, 0.45)",
                            },
                        }}
                      />
                    }
                    label={
                      <Box>
                        <Typography
                          sx={{
                            fontSize: "13px",
                            fontWeight: 500,
                            color: useJsonPipeline ? "rgba(139, 92, 246, 1)" : "#374151",
                            lineHeight: 1.3,
                          }}
                        >
                          JSON Pipeline
                        </Typography>
                        <Typography
                          sx={{ fontSize: "11px", color: "#9CA3AF", lineHeight: 1.3 }}
                        >
                          structured layout control
                        </Typography>
                      </Box>
                    }
                    sx={{ m: 0, gap: 0.5 }}
                  />
                </Box>
              </Tooltip>
            )}

            {/* Main Action Button */}
            <motion.div whileTap={{ scale: 0.99 }} style={{ flex: "1 1 100%" }}>
            <Button
              fullWidth
              variant="contained"
              onClick={handleProcessImage}
              disabled={
                isProcessing ||
                (engineType === "transformation" &&
                  (!uploadedImage || selectedPresets.length === 0)) ||
                (engineType === "creation" && !prompt.trim())
              }
              sx={{
                py: 1.2,
                borderRadius: "18px",
                textTransform: "none",
                fontSize: "14px",
                fontWeight: 600,
                bgcolor: "rgba(139, 92, 246, 1)",
                color: "#111827",
                boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
                transition: "filter 0.15s ease",
                "&:hover": {
                  bgcolor: "rgba(139, 92, 246, 1)",
                  filter: "brightness(0.94)",
                  boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
                },
                "&.Mui-disabled": {
                  background: "#FFFFFF",
                  color: "#9CA3AF",
                },
                flex: "1 1 100%",
              }}
            >
              {isProcessing ? (
                <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                  <CircularProgress size={20} color="inherit" />
                  Processing {selectedPresets.length} items...
                </Box>
              ) : (
                "Process & Enhance Media"
              )}
            </Button>
            </motion.div>
          </Box>

          {/* Column 2 - Image Preview */}
          <Box
            sx={{
              flex: 1,
              width: "100%",
              display: "flex",
              flexDirection: "column",
            }}
          >
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                mb: 1.5,
              }}
            >
              <Typography
                sx={{
                  fontSize: "15px",
                  fontWeight: 500,
                  color: "#111827",
                }}
              >
                Preview Pipeline
              </Typography>
              {previewUrl && processedImages.length > 0 && (
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => setShowOriginal(!showOriginal)}
                  sx={{
                    textTransform: "none",
                    fontSize: "13px",
                    fontWeight: 500,
                    borderColor: "#E5E7EB",
                    color: "#6B7280",
                    py: 0.5,
                    px: 1.5,
                    borderRadius: "8px",
                    "&:hover": {
                      borderColor: "rgba(139, 92, 246, 0.4)",
                      bgcolor: "rgba(139, 92, 246, 0.04)",
                      color: "rgba(139, 92, 246, 1)",
                    },
                  }}
                >
                  {showOriginal ? "View Results" : "View Original"}
                </Button>
              )}
            </Box>
            <Paper
              elevation={0}
              sx={{
                border: "1px solid rgba(17, 24, 39, 0.16)",
                borderRadius: "18px",
                p: { xs: 2, md: 3 },
                display: "flex",
                flexDirection: "column",
                alignItems: "stretch",
                justifyContent: "flex-start",
                minHeight: "280px",
                maxHeight: "440px",
                overflowY: "auto",
                position: "relative",
                boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
                "&::-webkit-scrollbar": {
                  width: "0px",
                  display: "none",
                },
                scrollbarWidth: "none",
                msOverflowStyle: "none",
              }}
            >
              {selectedPresets.length > 0 && !showOriginal ? (
                <Box
                  sx={{
                    width: "100%",
                    height: "100%",
                    display: "flex",
                    flexDirection: "column",
                    minHeight: 0,
                    overflow: "hidden",
                  }}
                >
                  <Box sx={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", mb: 1.5, flexShrink: 0 }}>
                    <Typography sx={{ fontSize: { xs: "13px", md: "14px" }, fontWeight: 500, color: "#111827" }}>
                      Output Array
                    </Typography>
                    <Typography sx={{ fontSize: "11px", color: "#9CA3AF" }}>
                      <SpecReadout size={11} color="#9CA3AF">
                        {processedImages.length}/{selectedPresets.length}
                      </SpecReadout>{" "}
                      complete
                    </Typography>
                  </Box>
                  <Box
                    sx={{
                      flex: 1,
                      overflowY: "auto",
                      minHeight: 0,
                      pb: 0.5,
                      display: "grid",
                      gridTemplateColumns: "repeat(auto-fill, minmax(150px, 1fr))",
                      gap: 1.25,
                      alignContent: "start",
                      "&::-webkit-scrollbar": { width: "6px" },
                      "&::-webkit-scrollbar-thumb": { background: "#D1D5DB", borderRadius: "4px" },
                    }}
                  >
                    {selectedPresets.map((presetId, idx) => {
                      const preset = presets.find((p) => p.id === presetId);
                      if (!preset) return null;
                      const match = processedImages.find((img) => img.ratio === preset.ratio);
                      const status: "pending" | "processing" | "done" = match
                        ? "done"
                        : isProcessing
                          ? "processing"
                          : "pending";
                      return (
                        <FadeIn key={presetId} delay={Math.min(idx, 8) * 0.03} style={{ height: "100%" }}>
                          <OutputPlate
                            label={preset.label}
                            ratio={preset.ratio}
                            status={status}
                            image={match || null}
                            onOpen={() =>
                              match &&
                              handleOpenModal({
                                url: match.url,
                                preset: match.preset,
                                ratio: match.ratio,
                                reportId: match.reportId,
                              })
                            }
                            onDownload={() => match && handleDownload(match.url, `${match.preset}-${match.ratio}.png`)}
                          />
                        </FadeIn>
                      );
                    })}
                  </Box>
                </Box>
              ) : previewUrl ? (
                <Box
                  sx={{
                    textAlign: "center",
                    width: "100%",
                    height: "100%",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <Box
                    component="img"
                    src={previewUrl}
                    alt="Preview"
                    sx={{
                      maxWidth: "100%",
                      maxHeight: { xs: "300px", md: "500px" },
                      width: "auto",
                      height: "auto",
                      objectFit: "contain",
                      borderRadius: "8px",
                      mb: 2,
                    }}
                  />
                  <Typography
                    sx={{
                      fontSize: { xs: "13px", md: "14px" },
                      fontWeight: 500,
                      color: "#374151",
                    }}
                  >
                    Original image ready
                  </Typography>
                  <Typography
                    sx={{
                      fontSize: { xs: "12px", md: "13px" },
                      color: "#9CA3AF",
                      mt: 0.25,
                    }}
                  >
                    Select presets on the left to start processing.
                  </Typography>
                </Box>
              ) : (
                <Box
                  sx={{
                    width: "100%",
                    height: "100%",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: 1.5,
                  }}
                >
                  <Box
                    sx={{
                      width: 56,
                      height: 56,
                      borderRadius: "16px",
                      background: "linear-gradient(135deg, rgba(7,89,133,0.08), rgba(139,92,246,0.05))",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      color: "rgba(139, 92, 246, 0.7)",
                    }}
                  >
                    <PhotoLibraryIcon sx={{ fontSize: 26 }} />
                  </Box>
                  <Typography
                    sx={{
                      fontSize: { xs: "13px", md: "14px" },
                      fontWeight: 500,
                      color: "#374151",
                      textAlign: "center",
                    }}
                  >
                    Nothing to preview yet
                  </Typography>
                  <Typography
                    sx={{
                      fontSize: { xs: "12px", md: "13px" },
                      color: "#9CA3AF",
                      textAlign: "center",
                      maxWidth: 280,
                    }}
                  >
                    {engineType === "creation"
                      ? "Enter a prompt and select presets to start generating."
                      : "Select an image and presets to start processing."}
                  </Typography>
                </Box>
              )}
            </Paper>
          </Box>
        </Box>
      </Container>

      {/* Full Image Preview Modal */}
      <Modal
        open={modalOpen}
        onClose={handleCloseModal}
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          p: 2,
        }}
      >
        <Box
          sx={{
            position: "relative",
            bgcolor: "white",
            borderRadius: "18px",
            p: 3,
            maxWidth: "90vw",
            maxHeight: "90vh",
            display: "flex",
            flexDirection: "column",
            outline: "none",
          }}
        >
          {/* Modal Header */}
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              mb: 2,
            }}
          >
            <Typography
              sx={{
                fontSize: "14px",
                fontWeight: 500,
                color: "#111827",
              }}
            >
              {selectedImage?.preset} ({selectedImage?.ratio})
            </Typography>
            <Box sx={{ display: "flex", gap: 1, alignItems: "center" }}>
              <ComplianceBadge reportId={selectedImage?.reportId} />
              <IconButton
                onClick={() =>
                  selectedImage &&
                  handleDownload(
                    selectedImage.url,
                    `${selectedImage.preset}-${selectedImage.ratio}.png`,
                  )
                }
                sx={{
                  bgcolor: "#FFFFFF",
                  "&:hover": {
                    bgcolor: "#E5E7EB",
                  },
                }}
              >
                <DownloadIcon sx={{ fontSize: 20, color: "#374151" }} />
              </IconButton>
              <IconButton
                onClick={handleCloseModal}
                sx={{
                  bgcolor: "#FFFFFF",
                  "&:hover": {
                    bgcolor: "#E5E7EB",
                  },
                }}
              >
                <CloseIcon sx={{ fontSize: 20, color: "#374151" }} />
              </IconButton>
            </Box>
          </Box>

          {/* Modal Image */}
          {selectedImage && (
            <Box
              sx={{
                width: "100%",
                height: "auto",
                maxHeight: "calc(90vh - 120px)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                overflow: "auto",
              }}
            >
              <Box
                component="img"
                src={selectedImage.url}
                alt={selectedImage.preset}
                sx={{
                  maxWidth: "100%",
                  maxHeight: "calc(90vh - 120px)",
                  width: "auto",
                  height: "auto",
                  objectFit: "contain",
                  borderRadius: "8px",
                }}
              />
            </Box>
          )}
        </Box>
      </Modal>

      {/* Credit Limit Exceeded Modal */}
      <Modal
        open={isLimitExceeded}
        onClose={() => setIsLimitExceeded(false)}
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          p: 2,
        }}
      >
        <PopIn>
        <Paper
          sx={{
            width: "100%",
            maxWidth: 450,
            borderRadius: "18px",
            border: "1px solid rgba(17, 24, 39, 0.16)",
            p: 4,
            textAlign: "center",
            position: "relative",
            overflow: "hidden",
            outline: "none",
            boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
          }}
        >
          <Box
            sx={{
              mb: 3,
              display: "inline-flex",
              p: 2,
              border: "1px solid rgba(139, 92, 246, 0.4)",
              borderRadius: "18px",
            }}
          >
            <AutoAwesomeIcon
              sx={{ fontSize: 32, color: "rgba(139, 92, 246, 1)" }}
            />
          </Box>

          <Typography
            sx={{ fontSize: "18px", fontWeight: 500, color: "#111827", mb: 1 }}
          >
            Infrastructure Upgrade Needed
          </Typography>

          <Typography
            variant="body2"
            sx={{ color: "#6B7280", mb: 4, lineHeight: 1.6 }}
          >
            Provision additional credits to continue high-density batch
            operations. Your current quota has been reached.
          </Typography>

          <Stack spacing={2}>
            <Button
              fullWidth
              variant="contained"
              onClick={() => {
                setIsLimitExceeded(false);
                window.location.href = "/pricing";
              }}
              sx={{
                py: 1.2,
                borderRadius: "18px",
                bgcolor: "rgba(139, 92, 246, 1)",
                color: "#111827",
                textTransform: "none",
                fontWeight: 600,
                fontSize: "14px",
                boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
                "&:hover": {
                  bgcolor: "rgba(139, 92, 246, 1)",
                  filter: "brightness(0.94)",
                  boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
                },
              }}
            >
              Provision Credits
            </Button>

            <Button
              fullWidth
              variant="text"
              onClick={() => setIsLimitExceeded(false)}
              sx={{
                py: 1.5,
                borderRadius: "18px",
                textTransform: "none",
                color: "#6B7280",
                fontWeight: 500,
                "&:hover": { bgcolor: "#FFFFFF" },
              }}
            >
              Maybe later
            </Button>
          </Stack>

          <Typography
            variant="caption"
            sx={{ display: "block", mt: 3, color: "#9CA3AF", fontWeight: 500 }}
          >
            Questions?{" "}
            <Box
              component="span"
              sx={{ color: "rgba(139, 92, 246, 1)", cursor: "pointer" }}
            >
              Talk to support
            </Box>
          </Typography>
        </Paper>
        </PopIn>
      </Modal>
      {/* Preset Limit Modal */}
      <Modal open={showPresetLimit}>
        <PopIn>
        <Paper
          elevation={0}
          sx={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            width: { xs: "90%", sm: 400 },
            borderRadius: "18px",
            border: "1px solid rgba(17, 24, 39, 0.16)",
            p: 4,
            textAlign: "center",
            outline: "none",
            bgcolor: "#FFFFFF",
            boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
            overflow: "hidden",
          }}
        >
          {/* Warning icon */}
          <Box
            sx={{
              width: 56,
              height: 56,
              borderRadius: "18px",
              border: "1px solid rgba(234, 88, 12, 0.4)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              mx: "auto",
              mb: 2,
            }}
          >
            <WarningAmberIcon sx={{ fontSize: 28, color: "rgba(234, 88, 12, 1)" }} />
          </Box>

          <Typography
            sx={{
              fontSize: "18px",
              fontWeight: 500,
              color: "#111827",
              mb: 1,
            }}
          >
            Selection Limit Reached
          </Typography>
          <Typography
            sx={{
              fontSize: "14px",
              color: "#6B7280",
              mb: 3,
              lineHeight: 1.6,
            }}
          >
            You can select up to <strong>{MAX_PRESETS} ratios</strong> at a
            time. Deselect one first to choose a different ratio.
          </Typography>

          <Button
            onClick={() => setShowPresetLimit(false)}
            fullWidth
            sx={{
              py: 1.5,
              borderRadius: "18px",
              fontSize: "14px",
              fontWeight: 600,
              textTransform: "none",
              bgcolor: "rgba(139, 92, 246, 1)",
              color: "#111827",
              boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
              "&:hover": {
                bgcolor: "rgba(139, 92, 246, 1)",
                filter: "brightness(0.94)",
              },
            }}
          >
            Got it
          </Button>
        </Paper>
        </PopIn>
      </Modal>
    </Box>
  );
};

export default ImageProcessor;
