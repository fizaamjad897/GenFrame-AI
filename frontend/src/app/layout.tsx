import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "./context/AuthContext";
import ThemeRegistry from "./components/ThemeRegistry";
import ToastProvider from "./components/ToastProvider";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

const outfit = Outfit({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-outfit",
});

export const metadata: Metadata = {
  title: "Visual Transformation Engine",
  description: "Process and resize images with custom presets",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${outfit.variable}`} suppressHydrationWarning>
        <ThemeRegistry>
          <AuthProvider>
            {children}
            <ToastProvider />
          </AuthProvider>
        </ThemeRegistry>
      </body>
    </html>
  );
}
