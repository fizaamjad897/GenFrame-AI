// GET ALL ORGS WITH USERS TYPES

export interface GetOrganisationsWithUsersInput {
  limit: number;
  page: number;
  searchTerm?: string | null;
}

export interface OrganisationUser {
  id: string;
  name: string;
  email: string;
  org_id: string;
  owner_name: string;
  phone: string;
  org_name: string;
  is_active: boolean;
  lastseen: string | null;
  rightData: any;
  role_id: string;
  role_name: string;
  custom_player_logo: string | null;
  org_type_name: string;
  max_player: number;
}

export interface Organisation {
  id: string;
  name: string;
  org_typeid: string;
  owner_name: string;
  custom_player_logo: string | null;
  logo: string | null;
  max_player: number;
  setup_player: number;
  is_active: boolean;
  parent_org_id: string | null;
  users: OrganisationUser[];
  industry: string;
  region: string;
  time_zone: string;
}

export interface GetAllOrganisationsWithUsersResponse {
  success: boolean;
  message: string;
  org: Organisation[];
  totalPages: number;
  currentPage: number;
  currentOrgMaxPlayers: number;
  currentOrgOfflinePlayers: number;
  currentOrgOnlinePlayers: number;
  currentOrgSetupPlayers: number;
  totalOrganisations: number;
}

//////////////////////////////////////////////////////////////

// CREATE ORG TYPES
export interface CreateOrganisationInput {
  owner_name: string;
  org_name: string;
  email: string;
  phone: string;
  industry: string;
  region: string;
  timeZone: string;
  logo?: string | null;
  selectedEngines?: string[];
  transformationCreditsThreshold?: number;
  transformationCreditPrice?: number;
  creationCreditsThreshold?: number;
  creationCreditPrice?: number;
}

// User type (same structure as used in other queries)
export interface OrganisationUser {
  id: string;
  name: string;
  email: string;
  org_id: string;
  owner_name: string;
  org_name: string;
  is_active: boolean;
  lastseen: string | null;
  rightData: any;
  role_id: string;
  role_name: string;
  custom_player_logo: string | null;
  org_type_name: string;
  max_player: number;
}

// Response type for the mutation
export interface CreateOrganisationResponse {
  success: boolean;
  message: string;
  token: string | null;
  user: OrganisationUser | null;
  requiresTwoFactor: boolean;
}

/////////////////////////////////////////////////////
// UPDATE ORGS TYPE
export interface UpdateOrgDataInput {
  name: string;
  custom_player_logo?: string | null;
  logo?: string | null;
  industry?: string | null;
  region?: string | null;
  timeZone?: string | null;
  max_player?: number | null;
}

export interface UpdateUserDataInput {
  name: string;
  phone?: string | null;
  country?: string | null;
}
export interface UpdateUserWithOrgInput {
  orgData: UpdateOrgDataInput;
  userData: UpdateUserDataInput;
  orgId: string;
  userId: string;
}
export interface UpdatedUser {
  id: string;
  name: string;
  email: string;
  org_id: string;
  owner_name: string;
  org_name: string;
  is_active: boolean;
  lastseen: string | null;
  rightData: any;
  role_id: string;
  role_name: string;
  custom_player_logo: string | null;
  org_type_name: string;
  max_player: number;
}

export interface UpdateUserWithOrganisationResponse {
  success: boolean;
  message: string;
  token: string | null;
  user: UpdatedUser | null;
  requiresTwoFactor: boolean;
}

////////////////////////////////////////////////////

// DELETE ORG TYPE

export interface DeleteOrganisationInput {
  orgIdToDelete: string;
}

export interface DeleteOrganisationResponse {
  success: boolean;
  message: string;
}

////////////////////////////////////////////////////////

// IMPERSONATE USER TYPES

export interface ImpersonateUserInput {
  userIdToImpersonate: string;
}

export interface ImpersonatedUser {
  id: string;
  name: string;
  email: string;
  org_id: string;
  owner_name: string;
  org_name: string;
  is_active: boolean;
  lastseen: string | null;
  rightData: any;
  role_id: string;
  role_name: string;
  custom_player_logo: string | null;
  org_type_name: string;
  max_player: number;
}
export interface ImpersonateUserResponse {
  success: boolean;
  message: string;
  token: string | null;
  user: ImpersonatedUser | null;
}

// EXIT IMPERSONATION //

export interface ExitImpersonationResponse {
  success: boolean;
  message: string;
  token: string | null;
  user: {
    id: string;
    name: string;
    email: string;
    org_id: string;
    owner_name: string;
    org_name: string;
    is_active: boolean;
    lastseen: string | null;
    rightData: any;
    role_id: string;
    role_name: string;
    custom_player_logo: string | null;
    org_type_name: string;
    max_player: number;
  } | null;
}

///////////////////////////////////////////////////////
