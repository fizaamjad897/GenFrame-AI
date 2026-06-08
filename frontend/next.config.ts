import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  // Reduce memory usage during build
  experimental: {
    optimizePackageImports: ['@mui/material', '@mui/icons-material'],
  },
};

export default nextConfig;
