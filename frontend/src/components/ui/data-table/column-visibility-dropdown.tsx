"use client";

import React from "react";
import { Column } from "./DataTable";
import { Checkbox } from "../checkbox";
import {
  Dropdown,
  DropdownButton,
  DropdownMenu,
  DropdownItem,
} from "../dropdown";
import { MenuItems } from "@headlessui/react";
import { Columns2, GripVertical, LucideIcon } from "lucide-react";

interface ColumnVisibilityDropdownProps {
  columns: Column<any>[];
  visibleColumns: string[];
  onColumnVisibilityChange: (columnKey: string, visible: boolean) => void;
  className?: string;
  icon?: LucideIcon;
  columnOrder?: string[];
  onColumnDragStart?: (index: number) => (e: React.DragEvent) => void;
  onColumnDragOver?: (index: number) => (e: React.DragEvent) => void;
  onColumnDrop?: () => void;
}

export function ColumnVisibilityDropdown({
  columns,
  visibleColumns,
  onColumnVisibilityChange,
  className,
  icon: Icon = Columns2,
  columnOrder,
  onColumnDragStart,
  onColumnDragOver,
  onColumnDrop,
}: ColumnVisibilityDropdownProps) {
  const ordered = (columnOrder || columns.map((c) => c.key))
    .map((k) => columns.find((c) => c.key === k))
    .filter(Boolean) as Column<any>[];

  return (
    <div className="relative">
      <Dropdown>
        <DropdownButton as="button" className="p-1 hover:bg-gray-100 rounded focus:outline-none">
          <Columns2 className="w-5 h-5 text-primary" />
        </DropdownButton>
        <DropdownMenu
          anchor="bottom start"
          className="min-w-0 p-1 bg-white border border-gray-200 shadow-lg rounded-xl z-[100] focus:outline-none scrollbar-hide"
        >
          {ordered.map((column, idx) => (
            <DropdownItem
              key={column.key}
              className="!text-body !text-gray-600 font-medium hover:bg-purple-25 rounded-lg scrollbar-hide"
              draggable
              onDragStart={
                onColumnDragStart ? onColumnDragStart(idx) : undefined
              }
              onDragOver={onColumnDragOver ? onColumnDragOver(idx) : undefined}
              onDrop={onColumnDrop}
            >
              <GripVertical className="w-4 h-4 text-gray-400 cursor-grab shrink-0" />
              <div className="flex items-center gap-2.5 min-w-0">
                <Checkbox
                  checked={visibleColumns.includes(column.key)}
                  onChange={(checked) =>
                    onColumnVisibilityChange(column.key, checked)
                  }
                />
                <span className="truncate">{column.label}</span>
              </div>
            </DropdownItem>
          ))}
        </DropdownMenu>
      </Dropdown>
    </div>
  );
}

export default ColumnVisibilityDropdown;
