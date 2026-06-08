"use client";

import React from "react";
import clsx from "clsx";
import { Checkbox } from "../checkbox";
import { TableCell } from "../table";
import { Column } from "./DataTable";

interface TableRowCellsProps<T = any> {
  row: T;
  rowId: string;
  index: number;
  visibleColumnData: Column<T>[];
  enableSelection?: boolean;
  isSelected: boolean;
  onRowSelect: (rowId: string, checked: boolean) => void;
  rowActions?: (row: T) => React.ReactNode;
  onRowClick?: (row: T) => void;
}

export function TableRowCells<T = any>({
  row,
  rowId,
  index,
  visibleColumnData,
  enableSelection = false,
  isSelected,
  onRowSelect,
  rowActions,
  onRowClick,
}: TableRowCellsProps<T>) {
  return (
    <>
      {enableSelection && (
        <TableCell className="w-12 !px-10">
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
      {visibleColumnData.map((column) => (
        <TableCell
          key={`${rowId}-${column.key}`}
          className={clsx(column.className, "px-7 py-4")}
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
    </>
  );
}

export default TableRowCells;
