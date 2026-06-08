"use client";

import React from "react";
import { Checkbox } from "../checkbox";
import { ColumnVisibilityDropdown } from "./column-visibility-dropdown";
import { TableHead, TableRow, TableHeader } from "../table";
import { TableHeaderCell } from "./table-header-cell";
import { Column } from "./DataTable";

interface DataTableHeaderProps<T = any> {
  // Column data
  columns: Column<T>[];
  visibleColumnData: Column<T>[];

  // Selection props
  enableSelection?: boolean;
  enableColumnVisibility?: boolean;
  enableBulkActions?: boolean;
  isAllSelected: boolean;
  isIndeterminate: boolean;
  onSelectAll: (checked: boolean) => void;
  onColumnVisibilityChange: (columnKey: string, visible: boolean) => void;
  visibleColumns: string[];

  // Sorting props
  sortColumn?: string;
  sortDirection?: "asc" | "desc";
  onSort?: (column: string) => void;

  // Column ordering (drag/drop)
  columnOrder?: string[];
  onColumnDragStart?: (index: number) => (e: React.DragEvent) => void;
  onColumnDragOver?: (index: number) => (e: React.DragEvent) => void;
  onColumnDrop?: () => void;
  onColumnDragEnd?: () => void;
  draggingColumn?: number | null;
  dragOverColumn?: number | null;

  // Actions
  rowActions?: boolean;
  // Resizing
  onColumnResize?: (columnKey: string, width: number) => void;
  enableColumnResize?: boolean;
  // Fixed columns
  enableFixedFirstColumn?: boolean;
}

export function DataTableHeader<T = any>({
  columns,
  visibleColumnData,
  enableSelection = false,
  enableColumnVisibility = false,
  enableBulkActions = false,
  isAllSelected,
  isIndeterminate,
  onSelectAll,
  onColumnVisibilityChange,
  visibleColumns,
  sortColumn,
  sortDirection,
  onSort,
  rowActions = false,
  columnOrder,
  onColumnDragStart,
  onColumnDragOver,
  onColumnDrop,
  onColumnDragEnd,
  draggingColumn,
  dragOverColumn,
  onColumnResize,
  enableColumnResize = true,
  enableFixedFirstColumn = true,
}: DataTableHeaderProps<T>) {
  return (
    <TableHead className="bg-gray-50">
      <TableRow>
        {enableSelection && (
          <TableHeader className="w-12">
            <div className="flex items-center gap-2">
              {enableColumnVisibility && (
                <ColumnVisibilityDropdown
                  columns={columns}
                  visibleColumns={visibleColumns}
                  onColumnVisibilityChange={onColumnVisibilityChange}
                  columnOrder={columnOrder}
                  onColumnDragStart={onColumnDragStart}
                  onColumnDragOver={onColumnDragOver}
                  onColumnDrop={onColumnDrop}
                />
              )}
              {enableBulkActions && (
                <Checkbox
                  aria-label="Select all rows"
                  checked={isAllSelected}
                  indeterminate={isIndeterminate}
                  onChange={(checked) => onSelectAll(checked)}
                />
              )}
            </div>
          </TableHeader>
        )}
        {visibleColumnData.map((column, idx) => (
          <TableHeaderCell
            key={column.key}
            columnKey={column.key}
            label={column.label}
            sortable={column.sortable}
            width={column.width}
            className={column.className}
            isSorted={sortColumn === column.key}
            sortDirection={
              sortColumn === column.key ? sortDirection : undefined
            }
            onSort={onSort}
            draggable
            onDragStart={onColumnDragStart ? onColumnDragStart(idx) : undefined}
            onDragOver={onColumnDragOver ? onColumnDragOver(idx) : undefined}
            onDrop={onColumnDrop}
            onDragEnd={onColumnDragEnd}
            isDragSource={draggingColumn === idx}
            isDragOver={dragOverColumn === idx}
            onResize={onColumnResize}
            enableResize={enableColumnResize}
            isFixed={enableFixedFirstColumn && idx === 0}
          />
        ))}
        {rowActions && <TableHeader className="w-1 px-2" />}
      </TableRow>
    </TableHead>
  );
}

export default DataTableHeader;
