"use client";

import React, { useState, useRef, useEffect } from "react";
import { clsx } from "clsx";
import {
  Search,
  Plus
} from "lucide-react";
import { InputWithButton } from "../input-with-button";
import { DataTableHeader } from "./data-table-header";
import { DataTableRow } from "./data-table-row";
import { DataTablePagination } from "./data-table-pagination";
import { DataTableBulkActions } from "./data-table-bulk-actions";
import { Table, TableBody } from "../table";

export interface Column<T = any> {
  key: string;
  label: string;
  sortable?: boolean;
  width?: string;
  render?: (value: any, row: T, index: number) => React.ReactNode;
  className?: string;
  visible?: boolean;
}

export interface DataTableProps<T = any> {
  // Data
  data: T[];
  isLoading: boolean;
  columns: Column<T>[];

  // Selection
  enableSelection?: boolean;
  selectedRows?: string[];
  onSelectionChange?: (selectedRows: string[]) => void;
  getRowId?: (row: T, index?: number) => string;

  // Search
  enableSearch?: boolean;
  searchPlaceholder?: string;
  searchValue?: string;
  onSearchChange?: (value: string) => void;

  // Filtering
  enableFilters?: boolean;
  onAddFilter?: () => void;
  filterComponent?: React.ReactNode;
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
  enablePagination?: boolean;
  currentPage?: number;
  totalPages?: number;
  totalItems?: number;
  pageSize?: number;
  pageSizeOptions?: number[];
  onPageChange?: (page: number) => void;
  onPageSizeChange?: (size: number) => void;

  // Styling
  className?: string;
  tableClassName?: string;

  // Actions
  onRowClick?: (row: T) => void;
  onRowRightClick?: (row: T) => void;
  rowActions?: (row: T) => React.ReactNode;

  // Bulk Actions
  enableBulkActions?: boolean;
  bulkActions?: React.ReactNode;
  onBulkDelete?: () => void;
  onBulkExport?: () => void;

  // Column Visibility
  enableColumnVisibility?: boolean;
  onColumnVisibilityChange?: (visibleColumns: string[]) => void;
  // Resizing
  enableColumnResize?: boolean;
  onColumnResize?: (columnKey: string, width: number) => void;
  // Fixed columns
  enableFixedFirstColumn?: boolean;

  // Empty State
  emptyStateComponent?: React.ReactNode;
}

export function DataTable<T = any>({
  data = [],
  isLoading,
  columns = [],

  // Selection
  enableSelection = false,
  selectedRows = [],
  onSelectionChange,
  getRowId = (row: T, index?: number) => `row-${index || 0}`,

  // Search
  enableSearch = false,
  searchPlaceholder = "Search...",
  searchValue = "",
  onSearchChange,

  // Filtering
  enableFilters = false,
  onAddFilter,
  filterComponent,
  filterChips,
  hasActiveFilters = false,

  // Sorting
  sortColumn,
  sortDirection,
  onSort,

  // Pagination
  enablePagination = false,
  currentPage = 1,
  totalPages = 1,
  totalItems = 0,
  pageSize = 10,
  pageSizeOptions = [10, 25, 50, 100],
  onPageChange,
  onPageSizeChange,

  // Styling
  className,
  tableClassName,

  // Actions
  onRowClick,
  onRowRightClick,
  rowActions,

  // Bulk Actions
  enableBulkActions = false,
  bulkActions,
  onBulkDelete,
  onBulkExport,

  // Column Visibility
  enableColumnVisibility = false,
  onColumnVisibilityChange,

  enableColumnResize = true,
  onColumnResize,
  enableFixedFirstColumn = true,
  emptyStateComponent,
}: DataTableProps<T>) {
  const [internalSearchValue, setInternalSearchValue] = useState(searchValue);
  const [visibleColumns, setVisibleColumns] = useState<string[]>(
    columns.filter((col) => col.visible !== false).map((col) => col.key)
  );

  // Dynamic container height so the table can extend to the bottom of the viewport
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [containerHeight, setContainerHeight] = useState<number | undefined>(
    undefined
  );

  const updateContainerHeight = () => {
    const el = containerRef.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const offsetBottom = 24; // leave a small gap from the bottom of the viewport
    const height = Math.max(200, window.innerHeight - rect.top - offsetBottom);
    setContainerHeight(height);
  };

  useEffect(() => {
    updateContainerHeight();
    window.addEventListener("resize", updateContainerHeight);
    window.addEventListener("orientationchange", updateContainerHeight);
    return () => {
      window.removeEventListener("resize", updateContainerHeight);
      window.removeEventListener("orientationchange", updateContainerHeight);
    };
  }, []);

  // Maintain a column order (all column keys). This controls rendering order
  const [columnOrder, setColumnOrder] = useState<string[]>(
    columns.map((col) => col.key)
  );

  // Keep columnOrder in sync if columns prop changes
  useEffect(() => {
    setColumnOrder((prev) => {
      const next = columns.map((c) => c.key);
      const merged = prev
        .filter((k) => next.includes(k))
        .concat(next.filter((k) => !prev.includes(k)));
      return merged.length ? merged : next;
    });
    setVisibleColumns((prev) => {
      const next = columns
        .filter((col) => col.visible !== false)
        .map((col) => col.key);
      return next;
    });
  }, [columns]);

  const handleSearchChange = (value: string) => {
    setInternalSearchValue(value);
    onSearchChange?.(value);
  };

  const handleSelectAll = (checked: boolean) => {
    if (!onSelectionChange) return;

    if (checked) {
      const allIds = data.map((row, index) =>
        typeof getRowId === "function" ? getRowId(row, index) : `row-${index}`
      );
      onSelectionChange(allIds);
    } else {
      onSelectionChange([]);
    }
  };

  const handleRowSelect = (rowId: string, checked: boolean) => {
    if (!onSelectionChange) return;

    if (checked) {
      onSelectionChange([...selectedRows, rowId]);
    } else {
      onSelectionChange(selectedRows.filter((id) => id !== rowId));
    }
  };

  const handleColumnVisibilityChange = (
    columnKey: string,
    visible: boolean
  ) => {
    const newVisibleColumns = visible
      ? [...visibleColumns, columnKey]
      : visibleColumns.filter((key) => key !== columnKey);

    setVisibleColumns(newVisibleColumns);
    onColumnVisibilityChange?.(newVisibleColumns);
  };

  // Drag/drop reordering state
  const dragSrcIndex = useRef<number | null>(null);
  const [draggingColumn, setDraggingColumn] = useState<number | null>(null);
  const [dragOverColumn, setDragOverColumn] = useState<number | null>(null);

  const reorderArray = (arr: string[], from: number, to: number) => {
    const next = arr.slice();
    const [moved] = next.splice(from, 1);
    next.splice(to, 0, moved);
    return next;
  };

  const handleColumnDragStart = (index: number) => (e: React.DragEvent) => {
    dragSrcIndex.current = index;
    setDraggingColumn(index);
    try {
      // draw a simple drag preview using canvas (no XML escaping needed)
      const label =
        (visibleColumnData && visibleColumnData[index]?.label) ||
        columns[index]?.label ||
        String(index);
      const padding = 12;
      const fontSize = 14;
      const font = `${fontSize}px Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial`;

      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d");
      if (ctx) {
        ctx.font = font;
        const textWidth = Math.ceil(ctx.measureText(label).width);
        const width = Math.max(80, textWidth + padding * 2);
        const height = 36;
        canvas.width = width;
        canvas.height = height;

        // background + border
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(0, 0, width, height);
        ctx.strokeStyle = "#eef0f5";
        ctx.lineWidth = 1;
        ctx.strokeRect(0.5, 0.5, width - 1, height - 1);

        // text
        ctx.fillStyle = "#716f88";
        ctx.font = font;
        ctx.textBaseline = "middle";
        ctx.fillText(label, padding, height / 2);

        const img = new Image();
        img.onload = () => {
          try {
            e.dataTransfer?.setDragImage(img, 12, height / 2);
          } catch (err) {
            // ignore
          }
        };
        img.src = canvas.toDataURL();
      }

      e.dataTransfer?.setData("text/plain", String(index));
      e.dataTransfer!.effectAllowed = "move";
    } catch (err) {
      // ignore in some browsers
    }
  };

  const handleColumnDragEnd = () => {
    dragSrcIndex.current = null;
    setDraggingColumn(null);
    setDragOverColumn(null);
  };

  const handleColumnDragOver = (index: number) => (e: React.DragEvent) => {
    e.preventDefault();
    const src = dragSrcIndex.current;
    if (src === null || src === index) return;
    setColumnOrder((prev) => reorderArray(prev, src, index));
    dragSrcIndex.current = index;
    setDragOverColumn(index);
  };

  const handleColumnDrop = () => {
    dragSrcIndex.current = null;
    onColumnVisibilityChange?.(
      visibleColumns
        .filter((k) => columnOrder.includes(k))
        .sort((a, b) => columnOrder.indexOf(a) - columnOrder.indexOf(b))
    );
    setDraggingColumn(null);
    setDragOverColumn(null);
  };

  const visibleColumnData = columnOrder
    .map((key) => columns.find((c) => c.key === key))
    .filter(Boolean)
    .filter((col) => visibleColumns.includes(col!.key)) as Column<T>[];

  const isAllSelected = data.length > 0 && selectedRows.length === data.length;
  const isIndeterminate =
    selectedRows.length > 0 && selectedRows.length < data.length;

  return (
    <div className={clsx("w-full", className)}>
      {/* Search and Filters */}
      {(enableSearch || enableFilters) && (
        <div className="flex items-center gap-3 mb-4">
          <div className="flex-1">
            <InputWithButton
              enableInput={enableSearch}
              enableAction={enableFilters}
              placeholder={searchPlaceholder}
              value={onSearchChange ? searchValue : internalSearchValue}
              onChange={handleSearchChange}
              onAction={onAddFilter}
              width={enableSearch ? "w-full md:w-[60%]" : undefined}
              inputClassName="text-sm"
              chips={filterChips}
              leftIcon={
                enableSearch ? (
                  <Search className="w-4 h-4 text-gray-400" />
                ) : undefined
              }
              rightButton={
                enableSearch && enableFilters
                  ? hasActiveFilters
                    ? {
                      icon: <Plus className="w-4 h-4 text-primary" />,
                      onClick: onAddFilter,
                      color: "white",
                      size: "xs",
                      iconOnly: true,
                      className:
                        "text-purple-600 hover:bg-purple-50 border border-gray-200",
                    }
                    : {
                      label: "Add Filter",
                      icon: <Plus className="w-4 h-4 text-primary" />,
                      onClick: onAddFilter,
                      color: "white",
                      size: "xs",
                      className:
                        "text-purple-600 hover:bg-purple-50 !border-gray-100 text-sm",
                    }
                  : undefined
              }
            />
          </div>

          {filterComponent}
        </div>
      )}

      {/* Table */}

      <div
        ref={containerRef}
        className="bg-white border border-gray-200 rounded-lg flex flex-col"
        style={containerHeight ? { height: `${containerHeight}px` } : undefined}
      >
        <div className="relative flex-1 overflow-auto scrollbar-hide min-w-0">
          {/* Main table content always rendered */}
          <Table className={clsx("w-full rounded-lg", tableClassName)}>
            <DataTableHeader
              columns={columns}
              visibleColumnData={visibleColumnData}
              enableSelection={enableSelection}
              enableColumnVisibility={enableColumnVisibility}
              enableBulkActions={enableBulkActions}
              isAllSelected={isAllSelected}
              isIndeterminate={isIndeterminate}
              onSelectAll={handleSelectAll}
              onColumnVisibilityChange={handleColumnVisibilityChange}
              visibleColumns={visibleColumns}
              columnOrder={columnOrder}
              onColumnDragStart={handleColumnDragStart}
              onColumnDragOver={handleColumnDragOver}
              onColumnDrop={handleColumnDrop}
              onColumnDragEnd={handleColumnDragEnd}
              draggingColumn={draggingColumn}
              dragOverColumn={dragOverColumn}
              rowActions={!!rowActions}
              sortColumn={sortColumn}
              sortDirection={sortDirection}
              onSort={onSort}
              onColumnResize={onColumnResize}
              enableColumnResize={enableColumnResize}
              enableFixedFirstColumn={enableFixedFirstColumn}
            />
            <TableBody>
              {data.map((row, index) => {
                const rowId =
                  typeof getRowId === "function"
                    ? getRowId(row, index)
                    : `row-${index}`;
                const isSelected = selectedRows.includes(rowId);

                return (
                  <DataTableRow
                    key={rowId}
                    row={row}
                    rowId={rowId}
                    index={index}
                    visibleColumnData={visibleColumnData}
                    draggingColumn={draggingColumn}
                    dragOverColumn={dragOverColumn}
                    enableSelection={enableSelection}
                    isSelected={isSelected}
                    onRowSelect={handleRowSelect}
                    rowActions={rowActions}
                    onRowRightClick={onRowRightClick}
                    onRowClick={onRowClick}
                    enableFixedFirstColumn={enableFixedFirstColumn}
                  />
                );
              })}
              
              {data.length === 0 && !isLoading && emptyStateComponent && (
                <tr>
                  <td colSpan={visibleColumns.length + (enableSelection ? 1 : 0) + (rowActions ? 1 : 0)} className="p-0 border-b-0 hidden md:table-cell">
                    <div className="flex w-full justify-center py-10">
                      {emptyStateComponent}
                    </div>
                  </td>
                  <td colSpan={100} className="p-0 border-b-0 md:hidden">
                    <div className="flex w-full justify-center py-10">
                      {emptyStateComponent}
                    </div>
                  </td>
                </tr>
              )}
            </TableBody>
          </Table>

          {/* Blur Overlay Loader */}
          {isLoading && (
            <div className="absolute inset-0 flex items-center rounded-lg justify-center bg-white/50 backdrop-blur-sm z-20">
              <div className="flex flex-col items-center">
                <div className="animate-spin rounded-full h-10 w-10 border-2 border-t-transparent border-purple-500 mb-3"></div>
              </div>
            </div>
          )}
        </div>

        {/* Pagination */}
        {enablePagination && (
          <DataTablePagination
            currentPage={currentPage}
            totalPages={totalPages}
            totalItems={totalItems}
            pageSize={pageSize}
            pageSizeOptions={pageSizeOptions}
            onPageChange={onPageChange}
            onPageSizeChange={onPageSizeChange}
          />
        )}

        {/* Bulk action footer (when rows selected) - rendered after pagination */}
        {enableBulkActions && selectedRows.length > 0 && (
          <DataTableBulkActions
            selectedRows={selectedRows}
            onSelectionChange={onSelectionChange!}
            onBulkDelete={onBulkDelete}
            onBulkExport={onBulkExport}
            additionalActions={bulkActions}
          />
        )}
      </div>
    </div>
  );
}

export default DataTable;
