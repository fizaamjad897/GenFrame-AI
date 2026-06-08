import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "./context/AuthContext";
import ThemeRegistry from "./components/ThemeRegistry";
import ToastProvider from "./components/ToastProvider";

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
      <body suppressHydrationWarning>
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
