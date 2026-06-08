"use client";

import React from "react";
import clsx from "clsx";
import { Checkbox } from "../checkbox";
import { TableRow, TableCell } from "../table";
import { Column } from "./DataTable";

interface DataTableRowProps<T = any> {
  // Row data
  row: T;
  rowId: string;
  index: number;

  // Column data
  visibleColumnData: Column<T>[];

  // Selection props
  enableSelection?: boolean;
  isSelected: boolean;
  onRowSelect: (rowId: string, checked: boolean) => void;

  // Actions
  rowActions?: (row: T) => React.ReactNode;

  // Interaction
  onRowClick?: (row: T) => void;
  onRowRightClick?: (row: T) => void;
  // Fixed columns
  enableFixedFirstColumn?: boolean;
  // drag visuals
  draggingColumn?: number | null;
  dragOverColumn?: number | null;
}

export function DataTableRow<T = any>({
  row,
  rowId,
  index,
  visibleColumnData,
  enableSelection = false,
  isSelected,
  onRowSelect,
  rowActions,
  onRowClick,
  onRowRightClick,
  enableFixedFirstColumn = true,
  draggingColumn,
  dragOverColumn,
}: DataTableRowProps<T>) {
  let clickTimeout: number | null = null;

  const handleClick = (row: T) => {
    if (clickTimeout) {
      window.clearTimeout(clickTimeout);
      clickTimeout = null;
    }

    clickTimeout = window.setTimeout(() => {
      onRowClick?.(row);
      clickTimeout = null;
    }, 200); // delay in ms
  };

  const handleRightClick = (row: T) => {
    if (clickTimeout) {
      window.clearTimeout(clickTimeout);
      clickTimeout = null;
    }
    onRowRightClick?.(row);
  };
  return (
    <TableRow
      key={rowId}
      className={clsx(
        "border-t border-gray-100 hover:bg-gray-50 transition-colors",
        (onRowClick || onRowRightClick) && "cursor-pointer",
      )}
      onClick={(e) => {
        e.stopPropagation();
        handleClick(row);
      }}
      onContextMenu={(e) => {
        e.preventDefault();
        e.stopPropagation();
        handleRightClick(row);
      }}
    >
      {enableSelection && (
        <TableCell className="!px-10">
          <div className="flex items-center gap-2">
            <Checkbox
              aria-label={`Select row ${index + 1}`}
              checked={isSelected}
              onChange={(checked) => onRowSelect(rowId, checked)}
              color="primary"
            />
          </div>
        </TableCell>
      )}
      {visibleColumnData.map((column, idx) => (
        <TableCell
          key={`${rowId}-${column.key}`}
          className={clsx(
            column.className,
            "px-5 py-4",
            // enableFixedFirstColumn && idx === 0 && "sticky left-0 z-10",
            draggingColumn === idx && "opacity-60",
            dragOverColumn === idx && "border-l-4 border-primary",
          )}
        >
          {column.render
            ? column.render(row[column.key as keyof T], row, index)
            : String(row[column.key as keyof T] || "")}
        </TableCell>
      ))}
      {rowActions && (
        <TableCell className="w-2 text-right py-4 px-4">
          <div className="inline-flex items-center justify-end w-4">
            {rowActions(row)}
          </div>
        </TableCell>
      )}
    </TableRow>
  );
}

export default DataTableRow;
