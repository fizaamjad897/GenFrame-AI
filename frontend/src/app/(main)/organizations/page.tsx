"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { decodeJwtToken } from "@/lib/jwtUtils";
import { OrganizationsPage } from "./OrganizationsPage";

export default function Organizations() {
  const router = useRouter();
  const [isAuthorized, setIsAuthorized] = useState(false);
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    const checkAuthorization = async () => {
      try {
        const token = localStorage.getItem("auth_token");
        if (!token) {
          router.push("/auth/signin");
          return;
        }

        const decoded = decodeJwtToken(token);
        
        // Check if user is authorized to access Organizations
        // Users in parent orgs can access (SubOrg users cannot)
        const orgTypeName = String(
          decoded?.orgTypeName || decoded?.orgType || decoded?.org_type_name || "",
        );
        const isParentOrgType = orgTypeName === "SuperOrg" || orgTypeName === "AppOwner";
        const isImpersonated = decoded?.impersonated === true;

        if (!isParentOrgType || isImpersonated) {
          // Don't set authorized, just redirect
          router.push("/dashboard");
          return;
        }

        // User is authorized
        setIsAuthorized(true);
      } catch (error) {
        console.error("Authorization check failed:", error);
        router.push("/auth/signin");
      } finally {
        setIsChecking(false);
      }
    };

    checkAuthorization();
  }, [router]);

  // Show nothing while checking or if not authorized
  if (isChecking || !isAuthorized) {
    return null;
  }

  return <OrganizationsPage />;
}
