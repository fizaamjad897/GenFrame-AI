import { jwtDecode } from "jwt-decode";

export interface DecodedToken {
  userId: string;
  impersonated?: boolean;
  orgId: string;
  userEmail: string;
  userName: string;
  userRole: string;
  userIsActive: boolean;
  userPhone: string;
  userCountry: string;
  userEnableAuth: boolean;
  orgName: string;
  orgOwnerName: string;
  orgType: string;
  orgMaxPlayer: number;
  orgRegion: string | null;
  orgTimeZone: string | null;
  orgIndustry: string | null;
  orgCustomPlayerLogo: boolean;
  iat: number;
  exp: number;
}

export function getDecodedToken(token: string): DecodedToken | null {
  try {
    const decoded: any = jwtDecode(token);

    // Map standard/snake_case claims to frontend camelCase interface if needed
    return {
      userId: decoded.userId || decoded.id || decoded.sub,
      userEmail: decoded.userEmail || decoded.email,
      userName: decoded.userName || decoded.name,
      userRole: decoded.userRole || decoded.role_name || decoded.role,
      userIsActive: decoded.userIsActive ?? decoded.is_active ?? false, // Ensure boolean
      userPhone: decoded.userPhone || decoded.phone || "",
      userCountry: decoded.userCountry || decoded.country || "",
      userEnableAuth: decoded.userEnableAuth ?? decoded.enable_auth ?? false,

      // Org fields
      orgId: decoded.orgId || decoded.org_id,
      orgName: decoded.orgName || decoded.org_name || "",
      orgOwnerName: decoded.orgOwnerName || decoded.owner_name || "",
      orgType: decoded.orgType || decoded.org_type_name || "",
      orgMaxPlayer: decoded.orgMaxPlayer || decoded.max_player || 0,
      orgRegion: decoded.orgRegion || decoded.region || null,
      orgTimeZone: decoded.orgTimeZone || decoded.timezone || null,
      orgIndustry: decoded.orgIndustry || decoded.industry || null,
      orgCustomPlayerLogo:
        decoded.orgCustomPlayerLogo ?? decoded.custom_player_logo ?? false,

      impersonated: decoded.impersonated,
      iat: decoded.iat,
      exp: decoded.exp,
    } as DecodedToken;
  } catch (error) {
    console.error("Invalid token:", error);
    return null;
  }
}

export function isTokenExpired(token: string): boolean {
  const decoded = getDecodedToken(token);
  if (!decoded?.exp) return true;
  const currentTime = Date.now() / 1000;
  return decoded.exp < currentTime;
}
