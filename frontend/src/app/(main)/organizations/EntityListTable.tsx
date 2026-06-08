"use client";

import React, { useState } from "react";
import { DataTable, Column } from "../../../components/ui/data-table/DataTable";
import { StatusBadge } from "../../../components/ui/status-badge";
import { UserAvatar } from "../../../components/ui/user-avatar";
import { RowActionsDropdown } from "../../../components/ui/data-table/row-actions-dropdown";
import { Eye } from "lucide-react";

// Generic data row type for entity listings
interface EntityRow {
  id: string;
  orgId: string;
  userId: string;
  name: string;
  email: string;
  status: "Active" | "Trial" | "Inactive";
  licenceUsed: number;
  licenceTotal: number;
  membersActive: number;
  membersTotal: number;
  created: string;
  nextCharge: string;
  avatar?: string | null;
  creditsUsed?: number;
  transformationCreditsUsed?: number;
  creationCreditsUsed?: number;
  estimatedCost?: number;
  transformationThreshold?: number;
  creationThreshold?: number;
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
  onToggleStatus?: (row: EntityRow) => void | Promise<void>;
  onBulkDelete?: () => void;
  enableSelection?: boolean;
  enableColumnVisibility?: boolean;
  enableColumnResize?: boolean;
  emptyStateComponent?: React.ReactNode;
}

export function EntityListTable({
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
  emptyStateComponent,
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
      label: "Organizations",
      sortable: true,
      width: columnWidths["name"] ? `${columnWidths["name"]}px` : undefined,
      render: (value, row) => {
        return (
          <UserAvatar name={row.name} email={row.email} avatar={row.avatar} />
        );
      },
    },
    {
      key: "status",
      label: "Status",
      className: "text-center",
      width: columnWidths["status"] ? `${columnWidths["status"]}px` : undefined,
      render: (value, row) => <StatusBadge status={row.status} />,
    },
    {
      key: "transformationCreditsUsed",
      label: "Transform Credits",
      visible: false,
      className:
        "text-center whitespace-normal break-words leading-tight !px-2",
      width: columnWidths["transformationCreditsUsed"]
        ? `${columnWidths["transformationCreditsUsed"]}px`
        : "130px",
      render: (value, row) => (
        <div className="text-subhead text-gray-900 font-regular text-center">
          {row.transformationCreditsUsed ?? 0}
        </div>
      ),
    },
    {
      key: "creationCreditsUsed",
      label: "Creation Credits",
      visible: false,
      className:
        "text-center whitespace-normal break-words leading-tight !px-2",
      width: columnWidths["creationCreditsUsed"]
        ? `${columnWidths["creationCreditsUsed"]}px`
        : "130px",
      render: (value, row) => (
        <div className="text-subhead text-gray-900 font-regular text-center">
          {row.creationCreditsUsed ?? 0}
        </div>
      ),
    },
    {
      key: "created",
      label: "Created",
      className: "text-left",
      sortable: true,
      width: columnWidths["created"]
        ? `${columnWidths["created"]}px`
        : undefined,
      render: (value, row) => (
        <div className="text-subhead text-gray-500 font-regular">
          {row.created}
        </div>
      ),
    },
    {
      key: "nextCharge",
      label: "Billing Date",
      className: "text-left",
      width: columnWidths["nextCharge"]
        ? `${columnWidths["nextCharge"]}px`
        : undefined,
      render: (value, row) => (
        <div className="text-subhead text-gray-500 font-regular">
          {row.nextCharge}
        </div>
      ),
    },
    {
      key: "transformationThreshold",
      label: "T. Threshold",
      visible: false,
      className:
        "text-center whitespace-normal break-words leading-tight !px-2",
      width: columnWidths["transformationThreshold"]
        ? `${columnWidths["transformationThreshold"]}px`
        : "110px",
      render: (value, row) => (
        <div className="text-subhead text-gray-500 font-regular text-center">
          {row.transformationThreshold ?? "—"}
        </div>
      ),
    },
    {
      key: "creationThreshold",
      label: "C. Threshold",
      visible: false,
      className:
        "text-center whitespace-normal break-words leading-tight !px-2",
      width: columnWidths["creationThreshold"]
        ? `${columnWidths["creationThreshold"]}px`
        : "110px",
      render: (value, row) => (
        <div className="text-subhead text-gray-500 font-regular text-center">
          {row.creationThreshold ?? "—"}
        </div>
      ),
    },
    {
      key: "estimatedCost",
      label: "Estimated Cost",
      className:
        "text-center whitespace-normal break-words leading-tight !px-2",
      sortable: true,
      width: columnWidths["estimatedCost"]
        ? `${columnWidths["estimatedCost"]}px`
        : "150px",
      render: (value, row) => (
        <div className="text-subhead text-gray-900 font-medium text-center">
          ${row.estimatedCost?.toFixed(2) || "0.00"}
        </div>
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
      emptyStateComponent={emptyStateComponent}
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
        <div className="flex items-center">
          {onView && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onView(row);
              }}
              className="p-1.5 rounded-md hover:bg-gray-100 cursor-pointer group relative"
            >
              <Eye className="w-6 h-6 text-gray-900" />
              <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 py-1 px-2 text-xs text-white bg-gray-800 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                Impersonate
              </span>
            </button>
          )}
          <RowActionsDropdown
            row={row}
            onEdit={onEdit}
            onToggleStatus={onToggleStatus}
            toggleStatusLabel={(item) =>
              item.status === "Active" ? "Deactivate" : "Activate"
            }
            // onExport={onExport}
            onDelete={onDelete}
          />
        </div>
      )}
      className=""
    />
  );
}

// Export with multiple generic names for flexibility
export { EntityListTable as EntityTable };
export { EntityListTable as ListTable };
export { EntityListTable as ContentTable };
export default EntityListTable;
