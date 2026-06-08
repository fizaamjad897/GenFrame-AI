"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { toast } from "react-toastify";
import { useAuth } from "@/app/context/AuthContext";
import { decodeJwtToken } from "@/lib/jwtUtils";
import { exitImpersonation } from "@/lib/organisationApi";

export default function ImpersonationHeader() {
  const router = useRouter();
  const { refreshUser, user } = useAuth();
  const [decodedToken, setDecodedToken] = useState<Record<string, any> | null>(
    null,
  );
  const [exitingImpersonation, setExitingImpersonation] = useState(false);

  // Decode JWT whenever user context changes or component mounts
  useEffect(() => {
    const token = localStorage.getItem("auth_token");
    if (token) {
      const decoded = decodeJwtToken(token);
      setDecodedToken(decoded);
    } else {
      setDecodedToken(null);
    }
  }, [user]); // Re-decode when user context updates

  const isImpersonated = decodedToken?.impersonated === true;
  const orgName = decodedToken?.orgName;
  const userEmail = decodedToken?.userEmail;

  // Log for debugging (debug level — hidden in production console by default)
  useEffect(() => {
    if (decodedToken) {
      console.debug("ImpersonationHeader token:", {
        impersonated: decodedToken.impersonated,
        orgName: decodedToken.orgName,
        userEmail: decodedToken.userEmail,
      });
    }
  }, [decodedToken]);

  const handleExitImpersonation = useCallback(async () => {
    setExitingImpersonation(true);
    try {
      const result = await exitImpersonation();
      toast.success("Exited impersonation successfully");

      // Restore original user's token
      localStorage.setItem("auth_token", result.token);
      // Clear cached user and fetch authoritative profile from backend.
      localStorage.removeItem("user");

      // Refresh user to update context
      await refreshUser();

      // Navigate back to organizations
      router.push("/organizations");
    } catch (err) {
      console.error("Error exiting impersonation:", err);
      toast.error(
        err instanceof Error ? err.message : "Failed to exit impersonation",
      );
    } finally {
      setExitingImpersonation(false);
    }
  }, [refreshUser, router]);

  if (!isImpersonated) {
    return null;
  }

  return (
    <div className="w-full bg-purple-600 text-white px-4 py-3 flex items-center justify-between shadow-md z-50">
      <div className="flex items-center gap-2">
        <span className="text-sm sm:text-base">👤 You are impersonating</span>
        <strong className="text-sm sm:text-base">
          {userEmail || orgName || "an organization"}
        </strong>
      </div>
      <button
        onClick={handleExitImpersonation}
        disabled={exitingImpersonation}
        className="px-3 py-1.5 sm:px-4 sm:py-2 bg-white text-purple-600 font-medium text-sm rounded hover:bg-gray-100 disabled:opacity-60 disabled:cursor-not-allowed transition-all cursor-pointer"
      >
        {exitingImpersonation ? "Exiting..." : "Exit Impersonation"}
      </button>
    </div>
  );
}
