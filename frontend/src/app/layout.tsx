import type { Metadata } from "next";
import { Inter, Outfit, JetBrains_Mono } from "next/font/google";
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

// Marketing surface: flat cream/near-black two-tone, monospace UI chrome,
// clean grotesk headline/body. Scoped via CSS variables only — the rest of
// the app keeps --font-inter / --font-outfit untouched.
const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  display: "swap",
  weight: ["400", "500", "700"],
  variable: "--font-panel-mono",
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
      <body className={`${inter.variable} ${outfit.variable} ${jetbrainsMono.variable}`} suppressHydrationWarning>
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
