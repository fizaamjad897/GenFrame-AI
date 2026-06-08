"use client";

import React, { useRef, useState } from "react";
import { clsx } from "clsx";
import {
  ChevronsUpDown,
  GripVertical,
  ChevronUp,
  ChevronDown,
} from "lucide-react";

interface TableHeaderCellProps {
  columnKey: string;
  label: string;
  sortable?: boolean;
  width?: string;
  className?: string;
  isSorted?: boolean;
  sortDirection?: "asc" | "desc";
  onSort?: (column: string) => void;
  draggable?: boolean;
  onDragStart?: (e: React.DragEvent) => void;
  onDragOver?: (e: React.DragEvent) => void;
  onDrop?: (e: React.DragEvent) => void;
  onResize?: (columnKey: string, width: number) => void;
  enableResize?: boolean;
  isFixed?: boolean;
  onDragEnd?: (e?: React.DragEvent) => void;
  isDragSource?: boolean;
  isDragOver?: boolean;
}

export function TableHeaderCell({
  columnKey,
  label,
  sortable = false,
  width,
  className,
  isSorted = false,
  sortDirection,
  onSort,
  draggable = false,
  onDragStart,
  onDragOver,
  onDrop,
  onDragEnd,
  isDragSource = false,
  isDragOver = false,
  onResize,
  enableResize = true,
  isFixed = true,
}: TableHeaderCellProps) {
  const thRef = useRef<HTMLTableCellElement>(null);
  const [isResizing, setIsResizing] = useState(false);

  const handleSortClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (sortable && onSort) {
      onSort(columnKey);
    }
  };

  const handleResizeStart = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    const startX = e.clientX;
    const startWidth = thRef.current?.offsetWidth || 0;
    const table = thRef.current?.closest("table");
    const tableWrapper = table?.parentElement;

    if (!tableWrapper) return;

    setIsResizing(true);
    tableWrapper.style.position = "relative";

    const overlay = document.createElement("div");
    overlay.style.cssText =
      "position:absolute;top:0;bottom:0;width:4px;background:#8B5CF6;z-index:10;pointer-events:none";

    const tableRect = tableWrapper.getBoundingClientRect();
    const thRect = thRef.current!.getBoundingClientRect();
    overlay.style.left = `${thRect.right - tableRect.left}px`;
    tableWrapper.appendChild(overlay);

    const handleMouseMove = (moveEvent: MouseEvent) => {
      const newWidth = Math.max(50, startWidth + moveEvent.clientX - startX);
      thRef.current!.style.width = `${newWidth}px`;

      const updatedTableRect = tableWrapper.getBoundingClientRect();
      const updatedThRect = thRef.current!.getBoundingClientRect();
      const linePos = Math.min(
        updatedThRect.right - updatedTableRect.left,
        updatedTableRect.width,
      );
      overlay.style.left = `${linePos}px`;
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      overlay.remove();
      onResize?.(columnKey, thRef.current!.offsetWidth);
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };

    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);
  };

  return (
    <th
      ref={thRef}
      draggable={draggable}
      onDragStart={(e) => {
        e.stopPropagation();
        onDragStart?.(e);
      }}
      onDragOver={(e) => {
        e.stopPropagation();
        onDragOver?.(e);
      }}
      onDrop={(e) => {
        e.stopPropagation();
        onDrop?.(e);
      }}
      onDragEnd={(e) => {
        e.stopPropagation();
        onDragEnd?.(e);
      }}
      className={clsx(
        className,
        "px-5 py-3 relative",
        isDragSource && "opacity-80 shadow-lg bg-gray-50",
        isDragOver && "border-l-4 border-primary",
        sortable && "select-none",
        // isFixed && "sticky left-0 bg-gray-50 z-10"
      )}
      style={width ? { width, minWidth: width } : undefined}
    >
      <div className="flex items-center gap-1">
        {/* Make the grip icon the visible drag handle. We stop propagation on drag events so clicking label still sorts. */}
        <div
          // grip icon is purely visual; the <th> is the draggable node
          draggable={false}
          onClick={(e) => e.stopPropagation()}
          className={clsx(
            "flex items-center pr-2",
            isDragSource ? "cursor-grabbing" : "cursor-grab",
          )}
          aria-hidden
        >
          <GripVertical
            className={clsx(
              "w-4 h-4 text-gray-500",
              isDragSource ? "text-primary" : "",
            )}
          />
        </div>
        <span className="text-body font-medium text-gray-500">{label}</span>
        {sortable && (
          <>
            {isSorted && sortDirection === "asc" && (
              <ChevronUp
                className="w-4 h-4 text-gray-900 cursor-pointer"
                onClick={handleSortClick}
              />
            )}
            {isSorted && sortDirection === "desc" && (
              <ChevronDown
                className="w-4 h-4 text-gray-900 cursor-pointer"
                onClick={handleSortClick}
              />
            )}
            {!isSorted && (
              <ChevronsUpDown
                className="w-4 h-4 text-gray-500 cursor-pointer"
                onClick={handleSortClick}
              />
            )}
          </>
        )}
      </div>

      {enableResize && !isFixed && (
        <div
          className="absolute top-0 right-0 w-1 h-full cursor-col-resize"
          onMouseDown={handleResizeStart}
        />
      )}
    </th>
  );
}

export default TableHeaderCell;
