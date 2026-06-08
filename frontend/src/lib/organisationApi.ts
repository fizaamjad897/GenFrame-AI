import { ApiException, getAuthToken } from "./api";

const ORG_API_BASE =
  process.env.NEXT_PUBLIC_ORG_MODULE_API_URL || "http://localhost:3001/api";

type OrgApiRequestOptions = RequestInit & {
  requireAuth?: boolean;
};

async function orgApiFetch<T>(
  path: string,
  options: OrgApiRequestOptions = {},
): Promise<T> {
  const { requireAuth = true, headers, ...rest } = options;

  const finalHeaders: Record<string, string> = {
    ...(headers as Record<string, string> | undefined),
  };

  if (requireAuth) {
    const token = getAuthToken();
    if (!token) {
      throw new ApiException("Not authenticated", 401);
    }
    finalHeaders.Authorization = `Bearer ${token}`;
  }

  if (rest.body && !(rest.body instanceof FormData)) {
    finalHeaders["Content-Type"] = "application/json";
  }

  let response: Response;
  try {
    response = await fetch(`${ORG_API_BASE}${path}`, {
      cache: "no-store",
      ...rest,
      headers: finalHeaders,
    });
  } catch (error) {
    throw new ApiException(
      error instanceof Error ? error.message : "Network error",
      0,
    );
  }

  if (!response.ok) {
    let errorMessage = `Request failed (${response.status})`;
    let errorDetail: string | undefined;

    try {
      const data = await response.json();
      errorDetail = data?.detail || data?.message;
      errorMessage = errorDetail || errorMessage;
    } catch {
      errorMessage = response.statusText || errorMessage;
    }

    throw new ApiException(errorMessage, response.status, errorDetail);
  }

  if (response.status === 204) {
    return {} as T;
  }

  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return (await response.json()) as T;
  }

  return (await response.text()) as unknown as T;
}

export interface OrganisationApiUser {
  id: string;
  name: string;
  email: string;
  org_id: string;
  is_active: boolean;
  lastseen?: string;
  role_name?: string;
  rightData?: string[];
  phone?: string;
  credits_used?: number;
  credits_allocated?: number;
  engine_access?: string[];
  billing_start_date?: string;
  billing_date?: string;
  estimated_cost?: number;
  // Per-engine fields
  transformation_credits_used?: number;
  creation_credits_used?: number;
  transformation_credit_price?: number;
  creation_credit_price?: number;
  transformation_threshold?: number;
  creation_threshold?: number;
  prev_month_transformation_credits_used?: number;
  prev_month_creation_credits_used?: number;
}

export interface OrganisationApiOrg {
  id: string;
  name: string;
  org_typeid?: string;
  owner_name?: string;
  custom_player_logo?: boolean;
  logo?: string;
  max_player?: number;
  is_active?: boolean;
  parent_org_id?: string;
  region?: string;
  time_zone?: string;
  industry?: string;
  users?: OrganisationApiUser[];
  selectedEngines?: string[];
  transformationCreditsThreshold?: number;
  transformationCreditPrice?: number;
  creationCreditsThreshold?: number;
  creationCreditPrice?: number;
  customerType?: 'PrePaid' | 'PostPaid';
  billingCycleDays?: number;
  created_at?: string;
  totalCreditsUsed?: number;
  estimatedCost?: number;
}

export interface OrganisationListResponse {
  organisations: OrganisationApiOrg[];
  totalPages: number;
  currentPage: number;
  totalOrganisations: number;
}

export interface OrganisationAuthResponse {
  token: string;
  user: OrganisationApiUser;
}

export interface CreateOrganisationPayload {
  email: string;
  org_name: string;
  owner_name: string;
  custom_player_logo?: boolean;
  region?: string;
  timeZone?: string;
  industry?: string;
  phone?: string;
  logo?: string | null;
  selectedEngines?: string[];
  transformationCreditsThreshold?: number;
  transformationCreditPrice?: number;
  creationCreditsThreshold?: number;
  creationCreditPrice?: number;
}

export interface UpdateOrganisationWithUserPayload {
  orgId: string;
  org_name?: string;
  region?: string;
  timeZone?: string;
  industry?: string;
  logo?: string | null;
  username?: string;
  phone?: string;
  country?: string;
}

export interface CreateUserPayload {
  username: string;
  email: string;
  password: string;
  rightsNames: string[];
  roleName: string;
}

export interface UpdateUserPayload {
  userId: string;
  username?: string;
  email?: string;
  phone?: string;
  country?: string;
  is_active?: boolean;
  rightsNames?: string[];
  roleName?: string;
}

export interface UpdateUserStatusPayload {
  userId: string;
  is_active: boolean;
}

export function orgSignup(payload: {
  name: string;
  email: string;
  password: string;
  org_name: string;
}) {
  return orgApiFetch<OrganisationAuthResponse>("/organisation/signup", {
    method: "POST",
    body: JSON.stringify(payload),
    requireAuth: false,
  });
}

export function orgSignin(payload: { email: string; password: string }) {
  return orgApiFetch<OrganisationAuthResponse>("/organisation/signin", {
    method: "POST",
    body: JSON.stringify(payload),
    requireAuth: false,
  });
}

export function forgotPassword(payload: { email: string }) {
  return orgApiFetch<{ success?: boolean; message?: string; token?: string }>(
    "/users/forgot-password",
    {
      method: "POST",
      body: JSON.stringify(payload),
      requireAuth: false,
    },
  );
}

export function resetPassword(payload: { token: string; newPassword: string }) {
  return orgApiFetch<{ success?: boolean; message?: string }>(
    "/users/reset-password",
    {
      method: "POST",
      body: JSON.stringify(payload),
      requireAuth: false,
    },
  );
}

export function listOrganisations(params: {
  search?: string;
  page?: number;
  limit?: number;
  filters?: string;
}) {
  const searchParams = new URLSearchParams();
  if (params.search) searchParams.set("search", params.search);
  if (params.filters) searchParams.set("filters", params.filters);
  searchParams.set("page", String(params.page ?? 1));
  searchParams.set("limit", String(params.limit ?? 25));

  return orgApiFetch<OrganisationListResponse>(
    `/organisation/list?${searchParams.toString()}`,
  );
}

export function createOrganisation(payload: CreateOrganisationPayload) {
  return orgApiFetch<{ success?: boolean; message?: string; token?: string; user?: OrganisationApiUser }>(
    "/organisation/create",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function updateOrganisationWithUser(payload: UpdateOrganisationWithUserPayload) {
  const { orgId, ...data } = payload;
  return orgApiFetch<{ success: boolean; message: string }>(
    `/organisation/${orgId}/with-user`,
    {
      method: "PUT",
      body: JSON.stringify(data),
    },
  );
}

export function deleteOrganisation(orgId: string) {
  return orgApiFetch<{ success: boolean; message: string }>(
    `/organisation/${orgId}`,
    { method: "DELETE" },
  );
}

export function impersonateUser(userId: string) {
  return orgApiFetch<{
    token: string;
    user?: { email?: string; id?: string; name?: string; [key: string]: any };
  }>(`/organisation/impersonate/${userId}`, { method: "POST" });
}

export function exitImpersonation() {
  return orgApiFetch<{
    token: string;
    user?: { email?: string; id?: string; name?: string; [key: string]: any };
  }>("/organisation/exit-impersonation", { method: "POST" });
}

export function createUser(payload: CreateUserPayload) {
  return orgApiFetch<{
    success: boolean;
    message?: string;
  }>("/users/create", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateUser(payload: UpdateUserPayload) {
  return orgApiFetch<{
    success: boolean;
    message?: string;
  }>("/users/update", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function updateUserStatus(payload: UpdateUserStatusPayload) {
  return orgApiFetch<{
    success: boolean;
    message?: string;
  }>("/users/status", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deleteUsers(userIds: string[]) {
  return orgApiFetch<{ success: boolean; message: string }>("/users", {
    method: "DELETE",
    body: JSON.stringify({ userIdToDelete: userIds }),
  });
}
