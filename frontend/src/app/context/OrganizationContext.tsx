"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from "react";

interface OrganizationContextType {
  organizationId: string | null;
  organizationName: string | null;
  isImpersonating: boolean;
  setOrganization: (orgId: string, orgName: string) => void;
  clearOrganization: () => void;
}

const OrganizationContext = createContext<OrganizationContextType | undefined>(
  undefined,
);

export function OrganizationProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [organizationId, setOrganizationId] = useState<string | null>(null);
  const [organizationName, setOrganizationName] = useState<string | null>(null);

  // Initialize from localStorage on mount
  useEffect(() => {
    const storedOrgId = localStorage.getItem("organizationId");
    const storedOrgName = localStorage.getItem("organizationName");
    if (storedOrgId && storedOrgName) {
      setOrganizationId(storedOrgId);
      setOrganizationName(storedOrgName);
    }
  }, []);

  const setOrganization = useCallback((orgId: string, orgName: string) => {
    setOrganizationId(orgId);
    setOrganizationName(orgName);
    localStorage.setItem("organizationId", orgId);
    localStorage.setItem("organizationName", orgName);
  }, []);

  const clearOrganization = useCallback(() => {
    setOrganizationId(null);
    setOrganizationName(null);
    localStorage.removeItem("organizationId");
    localStorage.removeItem("organizationName");
  }, []);

  const isImpersonating = organizationId !== null;

  return (
    <OrganizationContext.Provider
      value={{
        organizationId,
        organizationName,
        isImpersonating,
        setOrganization,
        clearOrganization,
      }}
    >
      {children}
    </OrganizationContext.Provider>
  );
}

export function useOrganization() {
  const context = useContext(OrganizationContext);
  if (context === undefined) {
    throw new Error(
      "useOrganization must be used within an OrganizationProvider",
    );
  }
  return context;
}
