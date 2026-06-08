"use client";

import { StatCard } from "@/components/ui/stat-card";
import { usePageHeader } from "@/app/context/PageHeaderContext";
import {
  Award,
  Building2,
  CalendarClock,
  ClipboardClock,
  FileCheck2,
  PlaySquare,
  UserCheck,
  UserRoundCog,
  Users,
} from "lucide-react";
import React, { useEffect, useMemo, useState } from "react";
import UserListTable from "./_components/UserListTable";
import { CreateUserModal } from "./_components/CreateUserModal";
import DeleteConfirmationModal from "@/components/shared/DeleteConfirmationModal";
import {
  deleteUsers,
  listOrganisations,
  updateUserStatus,
} from "@/lib/organisationApi";
import { getAuthToken } from "@/lib/api";
import { getDecodedToken } from "@/lib/authUtils";
// Mock Data
import { toast } from "react-toastify";
import { extractApiErrorMessage } from "@/lib/errorMessage";

interface UserRow {
  id: string;
  name: string;
  email: string;
  avatar?: string | null;
  organization: string;
  orgId?: string;
  role: "Admin" | "Manager" | "User";
  status: "Active" | "Trial" | "Inactive" | "Offline";
  lastActive: string;
  permissions?: string[];
}

const PageUser = () => {
  const { setHeader, resetHeader } = usePageHeader();
  const [users, setUsers] = useState<UserRow[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const [selectedRows, setSelectedRows] = useState<string[]>([]);
  const [searchValue, setSearchValue] = useState("");
  const [sortColumn, setSortColumn] = useState("");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);
  const [showFilterDialog, setShowFilterDialog] = useState<boolean>(false);
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [editingUser, setEditingUser] = useState<UserRow | null>(null);

  const fetchUsers = async () => {
    try {
      setIsLoading(true);
      const orgs = await listOrganisations({ page: 1, limit: 200 });

      const flattened: UserRow[] = (orgs.organisations || []).flatMap((org) =>
        (org.users || []).map((u) => ({
          id: u.id,
          name: u.name,
          email: u.email,
          organization: org.name,
          orgId: org.id,
          role:
            u.role_name === "owner" || u.role_name === "admin"
              ? "Admin"
              : "User",
          status: u.is_active ? "Active" : "Inactive",
          lastActive: u.lastseen || "—",
          permissions: u.rightData || [],
        })),
      );

      setUsers(flattened);
    } catch (error: any) {
      toast.error(extractApiErrorMessage(error, "Failed to fetch users"));
    } finally {
      setIsLoading(false);
    }
  };

  // Calculate stats from real data
  const stats = useMemo(() => {
    const totalUsers = users.length;
    const activeUsers = totalUsers;
    const totalAdmins = users.filter((u) => u.role === "Admin").length;

    return {
      totalUsers,
      activeUsers,
      totalAdmins,
    };
  }, [users]);

  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [userToDelete, setUserToDelete] = useState<UserRow | null>(null);

  const canManageSubOrgUsers = useMemo(() => {
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

  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortColumn(column);
      setSortDirection("asc");
    }
  };

  const handleExport = (row: UserRow) => console.log("EXPORT", row);
  const handleRowClick = (row: UserRow) => console.log("ROW CLICK", row);
  const handleView = async (row: UserRow) => console.log("VIEW", row);
  const handleEdit = (row: UserRow) => {
    setEditingUser(row);
    setShowCreateModal(true);
  };

  const handleDelete = (row: UserRow) => {
    setUserToDelete(row);
    setShowDeleteModal(true);
  };

  const handleToggleStatus = async (row: UserRow) => {
    const nextActive = row.status !== "Active";
    const toastId = toast.loading(
      `${nextActive ? "Activating" : "Deactivating"} user...`,
    );

    try {
      const result = await updateUserStatus({
        userId: row.id,
        is_active: nextActive,
      });
      toast.update(toastId, {
        render: result.message || "User status updated successfully",
        type: "success",
        isLoading: false,
        autoClose: 2000,
      });
      await fetchUsers();
    } catch (error: any) {
      toast.update(toastId, {
        render: extractApiErrorMessage(error, "Failed to update user status"),
        type: "error",
        isLoading: false,
        autoClose: 3500,
      });
    }
  };

  const handleBulkDelete = () => {
    setUserToDelete(null);
    setShowDeleteModal(true);
  };

  const handleConfirmDelete = async () => {
    setIsDeleting(true);
    if (userToDelete) {
      try {
        const result = await deleteUsers([userToDelete.id]);
        toast.success(result.message || "User deleted successfully");
        await fetchUsers();
        setSelectedRows((prev) => prev.filter((id) => id !== userToDelete.id));
      } catch (error: any) {
        toast.error(extractApiErrorMessage(error, "Failed to delete user"));
      }
    } else {
      try {
        const result = await deleteUsers(selectedRows);
        toast.success(
          result.message || `Successfully deleted ${selectedRows.length} users`,
        );
        setSelectedRows([]);
        await fetchUsers();
      } catch (error: any) {
        toast.error(extractApiErrorMessage(error, "Failed to delete users"));
      }
    }
    setShowDeleteModal(false);
    setUserToDelete(null);
    setIsDeleting(false);
  };

  const sortedData = useMemo(() => {
    const search = searchValue.toLowerCase();

    let filtered = users.filter(
      (item) =>
        item.name.toLowerCase().includes(search) ||
        item.email.toLowerCase().includes(search) ||
        item.organization.toLowerCase().includes(search),
    );

    if (sortColumn) {
      filtered.sort((a: any, b: any) => {
        const aVal = a[sortColumn];
        const bVal = b[sortColumn];

        if (aVal < bVal) return sortDirection === "asc" ? -1 : 1;
        if (aVal > bVal) return sortDirection === "asc" ? 1 : -1;
        return 0;
      });
    }

    return filtered;
  }, [users, searchValue, sortColumn, sortDirection]);

  useEffect(() => {
    setHeader({
      title: "Users",
      actionLabel: "Create User",
      onAction: () => setShowCreateModal(true),
    });
    void fetchUsers();
    return () => resetHeader();
  }, []);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 md:gap-6 mb-4">
        <StatCard
          icon={<Users className="h-6 w-6 text-primary" />}
          title="Total Users"
          value={stats.totalUsers.toString()}
          iconBgClass="bg-purple-25"
          loading={isLoading}
        />
        <StatCard
          icon={<UserCheck className="h-6 w-6 text-primary" />}
          title="Active Users"
          value={stats.activeUsers.toString()}
          iconBgClass="bg-purple-25"
          loading={isLoading}
        />
        <StatCard
          icon={<UserRoundCog className="h-6 w-6 text-primary" />}
          title="Admins"
          iconBgClass="bg-purple-25"
          value={stats.totalAdmins.toString()}
          loading={isLoading}
        />
        {/* <StatCard
                    icon={<ClipboardClock className="h-6 w-6 text-primary" />}
                    title="Pending Invites"
                    value="34"
                    iconBgClass="bg-purple-25"
                              loading={isLoading}

                /> */}
      </div>

      <div className="bg-background rounded-lg">
        <UserListTable
          data={sortedData}
          isLoading={isLoading}
          enableSelection
          selectedRows={selectedRows}
          onSelectionChange={setSelectedRows}
          enableColumnVisibility
          searchValue={searchValue}
          onSearchChange={setSearchValue}
          sortColumn={sortColumn}
          sortDirection={sortDirection}
          onSort={handleSort}
          currentPage={currentPage}
          totalPages={1}
          totalItems={sortedData.length}
          pageSize={pageSize}
          onPageChange={setCurrentPage}
          onPageSizeChange={(size) => {
            setPageSize(size);
            setCurrentPage(1);
          }}
          onAddFilter={() => setShowFilterDialog(true)}
          onRowClick={handleRowClick}
          onView={handleView}
          onExport={handleExport}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onToggleStatus={canManageSubOrgUsers ? handleToggleStatus : undefined}
          onBulkDelete={handleBulkDelete}
        />
        <CreateUserModal
          isOpen={showCreateModal}
          onClose={() => {
            setShowCreateModal(false);
            setEditingUser(null);
          }}
          initialData={editingUser}
          refetch={fetchUsers}
        />
        <DeleteConfirmationModal
          isOpen={showDeleteModal}
          onClose={() => {
            setShowDeleteModal(false);
            setUserToDelete(null);
          }}
          onSubmit={handleConfirmDelete}
          isLoading={isDeleting}
          itemType={userToDelete ? "User" : "Users"}
          itemName={
            userToDelete ? userToDelete.name : `${selectedRows.length} users`
          }
        />
      </div>
    </div>
  );
};

export default PageUser;
