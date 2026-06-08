"use client";

import React, { useState, useEffect, useMemo, useCallback } from "react";
import { clsx } from "clsx";
import { StatCard } from "../../../components/ui/stat-card";
import AgencyBar from "../../../components/ui/agency-bar";
import { EntityListTable } from "./EntityListTable";
import { Award, PlaySquare, FileCheck2, Building2 } from "lucide-react";
import {
  EmptyState,
  NoOrganizationsIllustration,
} from "../../../components/ui/empty-state";
import { usePageHeader } from "@/app/context/PageHeaderContext";
import { useAuth } from "@/app/context/AuthContext";
import { CreateOrganizationModal } from "./CreateOrganizationModal";
import SlideRightPanel from "../../../components/ui/slide-right-panel";
import AddFilterPanel from "../../../components/ui/add-filter/AddFilterPanel";
import { organizationFilterItems } from "./filterItems";
import { UpdateOrganizationModal } from "./UpdateOrganizationsModal";
import { toast } from "react-toastify";
import { useFilterState } from "@/hooks/useFilterState";
import {
  deleteOrganisation,
  impersonateUser,
  listOrganisations,
  OrganisationApiOrg,
  OrganisationListResponse,
  updateUserStatus,
} from "@/lib/organisationApi";
// import { useSyncUsersMutation } from "@/graphql/apis/genAiApi";

interface OrganizationsPageProps {
  className?: string;
}

interface TableRowData {
  id: string;
  orgId: string;
  userId: string;
  name: string;
  email: string;
  status: "Active" | "Inactive" | "Trial";
  licenceUsed: number;
  licenceTotal: number;
  membersActive: number;
  membersTotal: number;
  created: string;
  nextCharge: string;
  avatar?: string | null;
}

type StatusRow = {
  userId: string;
  status: "Active" | "Inactive" | "Trial";
  email?: string;
};

import DeleteConfirmationModal from "@/components/shared/DeleteConfirmationModal";
import { AgencyBarSkeleton } from "./AgencyBarSkeleton";
import { setCookie } from "cookies-next";
import { useRouter } from "next/navigation";
import { decodeJwtToken } from "@/lib/jwtUtils";
import { extractApiErrorMessage } from "@/lib/errorMessage";
import { getAuthToken } from "@/lib/api";
import { getDecodedToken } from "@/lib/authUtils";
import { Modal, ModalActions } from "@/components/ui/modal";

export function OrganizationsPage({ className }: OrganizationsPageProps) {
  const router = useRouter();

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showUpdateModal, setShowUpdateModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [orgToDelete, setOrgToDelete] = useState<OrganisationApiOrg | null>(
    null,
  );
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [statusTargetRow, setStatusTargetRow] = useState<StatusRow | null>(
    null,
  );
  const [statusTargetNextActive, setStatusTargetNextActive] = useState(false);
  const [isBulkDelete, setIsBulkDelete] = useState(false);

  const [searchValue, setSearchValue] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [selectedRows, setSelectedRows] = useState<string[]>([]);
  const [sortColumn, setSortColumn] = useState<string>("");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");
  const [showFilterDialog, setShowFilterDialog] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const { setHeader, resetHeader } = usePageHeader();
  const { user, refreshUser } = useAuth();
  const { selectedFilters, addFilter, getFilterChips } = useFilterState();
  const [selectedOrg, setSelectedOrg] = useState<OrganisationApiOrg | null>(
    null,
  );
  const [loading, setLoading] = useState(true);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [organisationsData, setOrganisationsData] =
    useState<OrganisationListResponse | null>(null);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(searchValue.trim());
    }, 500);
    return () => clearTimeout(handler);
  }, [searchValue]);

  const organizations: OrganisationApiOrg[] =
    organisationsData?.organisations ?? [];

  const refetch = useCallback(async () => {
    try {
      setLoading(true);
      const filterPayload = selectedFilters.map((f) => ({
        id: f.id,
        condition: f.condition,
        value: f.value,
      }));
      const response = await listOrganisations({
        search: debouncedSearch,
        page: currentPage,
        limit: pageSize,
        filters:
          filterPayload.length > 0 ? JSON.stringify(filterPayload) : undefined,
      });
      setOrganisationsData(response);
    } catch (err: any) {
      toast.error(extractApiErrorMessage(err, "Failed to fetch organizations"));
      setOrganisationsData(null);
    } finally {
      setLoading(false);
    }
  }, [debouncedSearch, currentPage, pageSize, selectedFilters]);

  useEffect(() => {
    void refetch();
  }, [refetch]);

  useEffect(() => {
    setHeader({
      title: "Organizations",
      actionLabel: "Create Organization",
      onAction: () => setShowCreateModal(true),
    });
    return () => resetHeader();
  }, [setHeader, setShowCreateModal]);

  const stats = useMemo(() => {
    // Calculate total credits: sum of all sub-org users + super org user credits
    const totalCreditsUsed = organizations.reduce((sum, org) => {
      return sum + (org.totalCreditsUsed || 0);
    }, 0);

    // Calculate total estimated cost using actual cost from each org
    const totalEstimatedCost = organizations.reduce((sum, org) => {
      return sum + (org.estimatedCost || 0);
    }, 0);

    // Calculate billing date (1st of next month)
    const today = new Date();
    const nextMonth = new Date(today.getFullYear(), today.getMonth() + 1, 1);
    const billingDate = nextMonth.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });

    const allUsers = organizations.flatMap((org) => org.users ?? []);
    const activeUsers = allUsers.filter((u) => u.is_active).length;
    const totalUsers = allUsers.length;

    return {
      totalOrganizations: organisationsData?.totalOrganisations ?? 0,
      totalCreditsUsed: totalCreditsUsed,
      estimatedCost: `$${totalEstimatedCost.toFixed(2)}`,
      billingDate: billingDate,
      membersActive: activeUsers,
      membersTotal: totalUsers,
    };
  }, [organisationsData, organizations]);

  const canManageUserStatus = useMemo(() => {
    const token = getAuthToken();
    if (!token) return false;
    const decoded = getDecodedToken(token);
    if (!decoded) return false;
    const role = decoded.userRole?.toLowerCase();
    const orgType = decoded.orgType;
    const isPrivilegedRole = role === "owner" || role === "admin";
    const isSuperOrg = orgType === "SuperOrg" || orgType === "AppOwner";
    return isPrivilegedRole && isSuperOrg;
  }, []);

  // Transform data - now user-centric, showing per-user data
  const tableData: TableRowData[] = useMemo(() => {
    const allRows: TableRowData[] = [];

    organizations.forEach((org) => {
      (org.users || []).forEach((user) => {
        const createdDate = user.billing_start_date
          ? new Date(user.billing_start_date).toLocaleDateString("en-US", {
              month: "short",
              day: "numeric",
              year: "numeric",
            })
          : "—";

        const today = new Date();
        const isPostpaid =
          (org as any).customerType?.toLowerCase() === "postpaid" ||
          (org as any).is_postpaid;

        let billingDate: string;
        if (isPostpaid) {
          const nextMonth = new Date(
            today.getFullYear(),
            today.getMonth() + 1,
            1,
          );
          billingDate = nextMonth.toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
            year: "numeric",
          });
        } else {
          const billingStart = user.billing_start_date
            ? new Date(user.billing_start_date)
            : today;
          const nextBill = new Date(billingStart);
          nextBill.setDate(nextBill.getDate() + 30);
          billingDate = nextBill.toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
            year: "numeric",
          });
        }

        allRows.push({
          id: user.id,
          orgId: org.id,
          userId: user.id,
          avatar: org.logo || null,
          name: org.name || user.name,
          email: user.email,
          status: user.is_active ? "Active" : "Inactive",
          licenceUsed: user.credits_used || 0,
          licenceTotal: user.credits_allocated || org.max_player || 0,
          membersActive: 1,
          membersTotal: 1,
          created: createdDate,
          nextCharge: billingDate,
          // Per-engine fields
          creditsUsed: user.credits_used || 0,
          transformationCreditsUsed: user.transformation_credits_used || 0,
          creationCreditsUsed: user.creation_credits_used || 0,
          estimatedCost: user.estimated_cost || 0,
          transformationThreshold: user.transformation_threshold || 0,
          creationThreshold: user.creation_threshold || 0,
        } as any);
      });
    });

    return allRows;
  }, [organizations]);

  const filteredData = tableData.filter((org) => {
    return true;
  });

  const sortedData = useMemo(() => {
    if (!sortColumn) return filteredData;
    return [...filteredData].sort((a, b) => {
      const aValue = (a as any)[sortColumn];
      const bValue = (b as any)[sortColumn];
      if (aValue < bValue) return sortDirection === "asc" ? -1 : 1;
      if (aValue > bValue) return sortDirection === "asc" ? 1 : -1;
      return 0;
    });
  }, [filteredData, sortColumn, sortDirection]);

  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortColumn(column);
      setSortDirection("asc");
    }
  };

  function handleRowClick(row: any) {
    return;
    // console.log(`Open Menu for Org`, { row });
  }
  // Removed syncUsers

  async function handleView(row: any) {
    const targetUserId = row.userId || row.id;
    const targetEmail = row.email;

    if (!targetUserId) {
      toast.error("Invalid organization data.");
      return;
    }

    toast.loading(`Impersonating ${targetEmail}...`);

    try {
      const result = await impersonateUser(targetUserId);
      console.log("Impersonation result:", result);

      toast.dismiss();

      if (result.token && result?.user?.email) {
        toast.success(`Now impersonating ${targetEmail}`);

        // Store the new impersonation token
        localStorage.setItem("auth_token", result.token);
        setCookie("token", result.token);
        // Clear stale cached user so dashboard doesn't render the previous user's billing mode.
        // We always hydrate the full impersonated profile from /users/me.
        localStorage.removeItem("user");

        // Refresh user context - will decode JWT and detect impersonation
        await refreshUser();

        router.push("/dashboard");
      } else {
        console.error("Unexpected impersonation response:", result);
        toast.error("Failed to impersonate user.");
      }
    } catch (err: any) {
      console.error("Error during impersonation:", err);
      toast.dismiss();
      toast.error(extractApiErrorMessage(err, "Failed to impersonate user."));
    }
  }

  const applyStatusChange = async (row: StatusRow, nextActive: boolean) => {
    const toastId = toast.loading(
      `${nextActive ? "Activating" : "Deactivating"} user...`,
    );

    try {
      const result = await updateUserStatus({
        userId: row.userId,
        is_active: nextActive,
      });
      toast.update(toastId, {
        render: result.message || "User status updated successfully",
        type: "success",
        isLoading: false,
        autoClose: 2000,
      });
      await refetch();
    } catch (err: any) {
      toast.update(toastId, {
        render: extractApiErrorMessage(err, "Failed to update user status"),
        type: "error",
        isLoading: false,
        autoClose: 3500,
      });
    }
  };

  const handleToggleStatus = async (row: StatusRow) => {
    const nextActive = row.status !== "Active";
    setStatusTargetRow(row);
    setStatusTargetNextActive(nextActive);
    setShowStatusModal(true);
  };

  const handleConfirmStatusChange = async () => {
    if (!statusTargetRow) return;
    setShowStatusModal(false);
    await applyStatusChange(statusTargetRow, statusTargetNextActive);
    setStatusTargetRow(null);
  };

  function handleExport(row: any) {
    console.log(`EXPORT`, { row });
  }

  function handleEdit(row: any) {
    const org = organizations.find((o) => o.id === row.orgId);
    if (!org) return;
    setSelectedOrg(org);
    setShowUpdateModal(true);
  }

  // Trigger Confirmation Modal
  function handleDelete(row: any) {
    const org = organizations.find((o) => o.id === row.orgId);
    if (!org) return;
    setOrgToDelete(org);
    setShowDeleteModal(true);
  }

  // Delete
  async function handleConfirmDelete() {
    if (!orgToDelete?.id) return;

    try {
      setDeleteLoading(true);
      const toastId = toast.loading("Deleting organization...");
      const result = await deleteOrganisation(orgToDelete.id);

      if (result.success) {
        toast.update(toastId, {
          render: result.message || "Organization deleted successfully!",
          type: "success",
          isLoading: false,
          autoClose: 3000,
        });
        setShowDeleteModal(false);
        setOrgToDelete(null);
        await refetch();
      } else {
        toast.update(toastId, {
          render: result.message || "Failed to delete organization.",
          type: "error",
          isLoading: false,
          autoClose: 4500,
        });
      }
    } catch (err: any) {
      console.error("Error deleting organization:", err);
      toast.dismiss();
      toast.error(
        extractApiErrorMessage(err, "Failed to delete organization."),
      );
    } finally {
      setDeleteLoading(false);
    }
  }

  // Bulk delete handler - shows confirmation modal
  function handleBulkDelete() {
    if (selectedRows.length === 0) return;
    setIsBulkDelete(true);
    setShowDeleteModal(true);
  }

  // Confirm bulk delete
  async function handleConfirmBulkDelete() {
    if (selectedRows.length === 0) return;

    try {
      setDeleteLoading(true);
      const toastId = toast.loading("Deleting organizations...");
      const selectedOrgIds = Array.from(
        new Set(
          tableData
            .filter((row) => selectedRows.includes(row.id))
            .map((row) => row.orgId),
        ),
      );

      const results = await Promise.all(
        selectedOrgIds.map((id) => deleteOrganisation(id)),
      );
      const failures = results.filter((r) => !r.success);
      if (failures.length) {
        toast.update(toastId, {
          render: `Deleted ${results.length - failures.length}/${results.length} organizations.`,
          type: "warning",
          isLoading: false,
          autoClose: 4500,
        });
      } else {
        toast.update(toastId, {
          render: `${selectedOrgIds.length} organization(s) deleted successfully!`,
          type: "success",
          isLoading: false,
          autoClose: 3000,
        });
      }
      setSelectedRows([]);
      setShowDeleteModal(false);
      setIsBulkDelete(false);
      await refetch();
    } catch (err: any) {
      console.error("Error deleting organizations:", err);
      toast.dismiss();
      toast.error(
        extractApiErrorMessage(err, "Failed to delete organizations."),
      );
    } finally {
      setDeleteLoading(false);
    }
  }

  const handleAddFilterCallback = (payload: {
    id: string;
    condition: string;
    value?: string;
  }) => {
    const filterItem = organizationFilterItems.find(
      (item) => item.id === payload.id,
    );
    if (filterItem) {
      addFilter({
        id: payload.id,
        title: filterItem.title,
        icon: filterItem.icon,
        condition: payload.condition,
        value: payload.value,
      });
    }
  };

  return (
    <>
      <div className={clsx("flex flex-col gap-4 h-full", className)}>
        {/* Stat Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 md:gap-6">
          <StatCard
            icon={<Building2 className="h-6 w-6 text-primary" />}
            title="Total Organizations"
            value={stats.totalOrganizations.toLocaleString()}
            iconBgClass="bg-purple-25"
            loading={loading}
          />
          <StatCard
            icon={<Award className="h-6 w-6 text-primary" />}
            title="Credits Used"
            value={stats.totalCreditsUsed.toLocaleString()}
            iconBgClass="bg-purple-25"
            loading={loading}
          />
          <StatCard
            icon={<PlaySquare className="h-6 w-6 text-primary" />}
            title="Estimated Cost"
            iconBgClass="bg-purple-25"
            value={stats.estimatedCost}
            loading={loading}
          />
          <StatCard
            icon={<FileCheck2 className="h-6 w-6 text-primary" />}
            title="Billing Date"
            value={stats.billingDate}
            iconBgClass="bg-purple-25"
            loading={loading}
          />
        </div>

        {/* Agency Bar */}
        {!organisationsData && loading ? (
          <AgencyBarSkeleton />
        ) : (
          <AgencyBar
            name={user?.fullName || "Your Organization"}
            email={user?.email || ""}
            status={"Active"}
            creditsUsed={stats.totalCreditsUsed}
            creditsTotal={stats.totalCreditsUsed}
            billingDate={stats.billingDate}
            avatarSrc="/Avatar.svg"
          />
        )}

        {/* Table */}
        <div className="bg-background rounded-lg">
          <EntityListTable
            emptyStateComponent={
              !loading && organizations.length === 0 ? (
                <EmptyState
                  title="No organizations found"
                  description="Start by creating your first organization."
                  actionLabel="Create Organization"
                  illustration={<NoOrganizationsIllustration />}
                  className="flex-1 border-none shadow-none"
                />
              ) : undefined
            }
            data={sortedData}
            isLoading={loading}
            enableSelection
            selectedRows={selectedRows}
            onSelectionChange={setSelectedRows}
            enableColumnVisibility
            searchValue={searchValue}
            onSearchChange={(v) => setSearchValue(v)}
            sortColumn={sortColumn}
            sortDirection={sortDirection}
            onSort={handleSort}
            currentPage={currentPage}
            totalPages={organisationsData?.totalPages ?? 1}
            totalItems={organisationsData?.totalOrganisations ?? 0}
            pageSize={pageSize}
            onPageChange={setCurrentPage}
            onPageSizeChange={(size) => {
              setPageSize(size);
              setCurrentPage(1);
            }}
            onAddFilter={() => setShowFilterDialog(true)}
            filterChips={getFilterChips()}
            hasActiveFilters={selectedFilters.length > 0}
            onRowClick={handleRowClick}
            onView={handleView}
            onExport={handleExport}
            onEdit={handleEdit}
            onDelete={handleDelete}
            onToggleStatus={
              canManageUserStatus ? handleToggleStatus : undefined
            }
            onBulkDelete={handleBulkDelete}
          />

          {/* Filter Panel */}
          <SlideRightPanel
            isOpen={showFilterDialog}
            onClose={() => setShowFilterDialog(false)}
            width="w-[420px]"
          >
            <AddFilterPanel
              items={organizationFilterItems}
              onClose={() => setShowFilterDialog(false)}
              onAddFilter={handleAddFilterCallback}
            />
          </SlideRightPanel>
        </div>
      </div>

      {/*  Create Modal */}
      <CreateOrganizationModal
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false);
          void refetch();
        }}
        refetch={refetch}
      />
      {/* Update Modal */}
      <UpdateOrganizationModal
        isOpen={showUpdateModal}
        selectedOrg={selectedOrg}
        onClose={() => {
          setShowUpdateModal(false);
          setSelectedOrg(null);
        }}
        refetch={refetch}
      />

      {/* Delete Confirmation Modal */}
      <DeleteConfirmationModal
        isOpen={showDeleteModal}
        onClose={() => {
          setShowDeleteModal(false);
          setOrgToDelete(null);
          setIsBulkDelete(false);
        }}
        onSubmit={isBulkDelete ? handleConfirmBulkDelete : handleConfirmDelete}
        itemName={
          isBulkDelete
            ? `${selectedRows.length} organization(s)`
            : orgToDelete?.name
        }
        itemType="organization"
        isLoading={deleteLoading}
      />

      {/* Deactivate Confirmation Modal */}
      <Modal
        isOpen={showStatusModal}
        onClose={() => {
          setShowStatusModal(false);
          setStatusTargetRow(null);
        }}
        title={statusTargetNextActive ? "Activate user" : "Deactivate user"}
        footer={
          <ModalActions
            onCancel={() => {
              setShowStatusModal(false);
              setStatusTargetRow(null);
            }}
            onSubmit={handleConfirmStatusChange}
            submitLabel={statusTargetNextActive ? "Activate" : "Deactivate"}
          />
        }
      >
        <div className="flex flex-col items-center text-center space-y-3 py-2">
          <div
            className={`flex items-center justify-center w-12 h-12 rounded-full ${
              statusTargetNextActive ? "bg-green-100" : "bg-yellow-100"
            }`}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className={`h-6 w-6 ${
                statusTargetNextActive ? "text-green-600" : "text-yellow-600"
              }`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v4m0 4h.01M21 12A9 9 0 113 12a9 9 0 0118 0z"
              />
            </svg>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {statusTargetNextActive
                ? "Are you sure you want to activate this user?"
                : "Are you sure you want to deactivate this user?"}
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              {statusTargetNextActive
                ? "They will be able to sign in again."
                : "They will not be able to sign in until reactivated."}
              {statusTargetRow?.email && (
                <>
                  <br />
                  <span className="font-medium text-gray-800">
                    {statusTargetRow.email}
                  </span>
                </>
              )}
            </p>
          </div>
        </div>
      </Modal>
    </>
  );
}
