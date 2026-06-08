"use client";

import React from "react";
import { Trash, Download, EllipsisVertical } from "lucide-react";
import { Badge } from "../badge";

export interface DataTableBulkActionsProps {
  selectedRows: string[];
  onSelectionChange: (selectedRows: string[]) => void;
  onBulkDelete?: () => void;
  onBulkExport?: () => void;
  additionalActions?: React.ReactNode;
}

export function DataTableBulkActions({
  selectedRows,
  onSelectionChange,
  onBulkDelete,
  onBulkExport,
  additionalActions,
}: DataTableBulkActionsProps) {
  return (
    <div className="flex items-center justify-between px-4 py-4 border-t border-gray-200 !rounded-b-lg bg-white overflow-x-auto">
      <div className="flex items-center gap-3 mx-6">
        {/* Badge showing count */}
        <Badge className="!bg-gray-900 !text-background !shadow-sm !min-w-[20px] !h-5 w-5 !px-0 !py-0 text-xs flex items-center justify-center">
          {selectedRows.length}
        </Badge>

        <div className="w-px h-8 bg-gray-200" />

        {/* Deselect All text */}
        <button
          type="button"
          onClick={() => onSelectionChange([])}
          className="text-subhead text-purple-300 ml-2 cursor-pointer font-semibold"
        >
          Deselect All
        </button>
      </div>

      <div className="flex items-center gap-3 mx-6">
        <button
          type="button"
          onClick={() => onBulkDelete?.()}
          className="inline-flex items-center gap-2 text-purple-300 text-subhead font-semibold px-2 py-1 bg-transparent border-0 hover:bg-transparent focus:outline-none cursor-pointer"
        >
          <Trash className="w-4 h-4" />
          Delete
        </button>

        {/* <button
          type="button"
          onClick={() => onBulkExport?.()}
          className="inline-flex items-center gap-2 text-purple-300 text-subhead font-semibold px-2 py-1 bg-transparent border-0 hover:bg-transparent focus:outline-none cursor-pointer"
        >
          <Download className="w-4 h-4" />
          Export
        </button> */}

        {/* Three-dots bordered button */}
        {/* <button
          type="button"
          className="inline-flex items-center justify-center rounded-md border border-gray-200 w-8 h-8 text-gray-600 hover:bg-gray-50"
        >
          <EllipsisVertical className="w-4 h-4" />
        </button> */}

        {additionalActions}
      </div>
    </div>
  );
}

export default DataTableBulkActions;
