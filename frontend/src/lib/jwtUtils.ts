/**
 * Decode JWT token without verification (frontend use only)
 * This is safe because authentication is verified on the backend
 */
export function decodeJwtToken(token: string): Record<string, any> | null {
  try {
    const parts = token.split(".");
    if (parts.length !== 3) return null;

    // Decode the payload (second part) using base64
    const decoded = JSON.parse(
      atob(parts[1].replace(/-/g, "+").replace(/_/g, "/")),
    );
    return decoded;
  } catch (error) {
    console.error("Error decoding JWT token:", error);
    return null;
  }
}

/**
 * Check if user is impersonated by reading JWT token
 */
export function isUserImpersonated(token: string): boolean {
  const decoded = decodeJwtToken(token);
  return decoded?.impersonated === true;
}

/**
 * Get organization info from JWT token
 */
export function getOrgFromToken(
  token: string,
): { id: string; name: string } | null {
  const decoded = decodeJwtToken(token);
  if (decoded?.orgId && decoded?.orgName) {
    return {
      id: decoded.orgId,
      name: decoded.orgName,
    };
  }
  return null;
}

/**
 * Get user info from JWT token
 */
export function getUserFromToken(token: string): Record<string, any> | null {
  return decodeJwtToken(token);
}
