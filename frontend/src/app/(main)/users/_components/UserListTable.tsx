"use client";

import DataTable, { Column } from "@/components/ui/data-table/DataTable";
import RowActionsDropdown from "@/components/ui/data-table/row-actions-dropdown";
import StatusBadge from "@/components/ui/status-badge";
import UserAvatar from "@/components/ui/user-avatar";
import React, { useState } from "react";

// Generic data row type for entity listings
interface EntityRow {
  id: string;

  // User column
  name: string;
  email: string;
  avatar?: string | null;

  // Table columns
  organization: string;
  role: "Admin" | "Manager" | "User";
  status: "Active" | "Trial" | "Inactive" | "Offline";
  lastActive: string;
}

interface EntityListTableProps {
  data: EntityRow[];
  isLoading: boolean;
  selectedRows?: string[];
  onSelectionChange?: (selectedRows: string[]) => void;

  // Search
  searchValue?: string;
  onSearchChange?: (value: string) => void;

  // Filters
  onAddFilter?: () => void;
  filterChips?: {
    id: string;
    label: string;
    icon?: React.ReactNode;
    onRemove?: () => void;
  }[];
  hasActiveFilters?: boolean;

  // Sorting
  sortColumn?: string;
  sortDirection?: "asc" | "desc";
  onSort?: (column: string) => void;

  // Pagination
  currentPage?: number;
  totalPages?: number;
  totalItems?: number;
  pageSize?: number;
  onPageChange?: (page: number) => void;
  onPageSizeChange?: (size: number) => void;

  onRowClick?: (row: EntityRow) => void;
  onView?: (row: EntityRow) => void;
  onExport?: (row: EntityRow) => void;
  onDelete?: (row: EntityRow) => void;
  onEdit?: (row: EntityRow) => void;
  onToggleStatus?: (row: EntityRow) => void;
  onBulkDelete?: () => void;
  enableSelection?: boolean;
  enableColumnVisibility?: boolean;
  enableColumnResize?: boolean;
}

export function UserListTable({
  data,
  isLoading,
  selectedRows = [],
  onSelectionChange,
  searchValue = "",
  onSearchChange,
  onAddFilter,
  filterChips,
  hasActiveFilters = false,
  sortColumn,
  sortDirection,
  onSort,
  currentPage = 1,
  totalPages = 1,
  totalItems = data.length,
  pageSize = 100,
  onPageChange,
  onPageSizeChange,
  onRowClick,
  onView,
  onExport,
  onEdit,
  onDelete,
  onToggleStatus,
  onBulkDelete,
  enableSelection = true,
  enableColumnVisibility = true,
  enableColumnResize = true,
}: EntityListTableProps) {
  const [columnWidths, setColumnWidths] = useState<Record<string, number>>({});

  const handleColumnResize = (columnKey: string, width: number) => {
    setColumnWidths((prev) => ({
      ...prev,
      [columnKey]: width,
    }));
  };

  const columns: Column<EntityRow>[] = [
    {
      key: "name",
      label: "User",
      sortable: true,
      width: columnWidths["name"] ? `${columnWidths["name"]}px` : undefined,
      render: (_, row) => (
        <UserAvatar name={row.name} email={row.email} avatar={row.avatar} />
      ),
    },
    {
      key: "organization",
      label: "Organization",
      sortable: true,
      width: columnWidths["organization"]
        ? `${columnWidths["organization"]}px`
        : undefined,
      render: (_, row) => (
        <div className="text-subhead text-gray-500">{row.organization}</div>
      ),
    },
    {
      key: "role",
      label: "Role",
      sortable: true,
      width: columnWidths["role"] ? `${columnWidths["role"]}px` : undefined,
      render: (_, row) => (
        <div className="text-subhead text-gray-500">{row.role}</div>
      ),
    },
    {
      key: "status",
      label: "Status",
      className: "text-center",
      width: columnWidths["status"] ? `${columnWidths["status"]}px` : undefined,
      render: (_, row) => <StatusBadge status={row.status} />,
    },
    {
      key: "lastActive",
      label: "Last Active",
      width: columnWidths["lastActive"]
        ? `${columnWidths["lastActive"]}px`
        : undefined,
      render: (_, row) => (
        <div className="text-subhead text-gray-500">{row.lastActive}</div>
      ),
    },
  ];

  return (
    <DataTable
      data={data}
      onBulkDelete={onBulkDelete}
      isLoading={isLoading}
      columns={columns}
      // Selection
      enableSelection={true}
      selectedRows={selectedRows}
      onSelectionChange={onSelectionChange}
      getRowId={(row) => row.id}
      // Search
      enableSearch={true}
      searchPlaceholder="Search by org name, owner email, region."
      searchValue={searchValue}
      onSearchChange={onSearchChange}
      // Filters
      enableFilters={true}
      onAddFilter={onAddFilter}
      filterChips={filterChips}
      hasActiveFilters={hasActiveFilters}
      // Sorting
      sortColumn={sortColumn}
      sortDirection={sortDirection}
      onSort={onSort}
      // Column Visibility
      enableColumnVisibility={enableColumnVisibility}
      // Column Resizing
      enableColumnResize={enableColumnResize}
      onColumnResize={handleColumnResize}
      // Pagination
      enablePagination={true}
      currentPage={currentPage}
      totalPages={totalPages}
      totalItems={totalItems}
      pageSize={pageSize}
      pageSizeOptions={[25, 50, 100, 200]}
      onPageChange={onPageChange}
      onPageSizeChange={onPageSizeChange}
      // Bulk Actions
      enableBulkActions={true}
      // Actions
      onRowClick={onRowClick}
      rowActions={(row) => (
        <RowActionsDropdown
          row={row}
          onEdit={onEdit}
          onToggleStatus={onToggleStatus}
          toggleStatusLabel={(item) =>
            item.status === "Active" ? "Deactivate" : "Activate"
          }
          onDelete={onDelete}
        />
      )}
      className=""
    />
  );
}

export default UserListTable;
