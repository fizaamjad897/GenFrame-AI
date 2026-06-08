"use client";

import React from "react";
import { Select } from "../select";
import {
  Pagination,
  PaginationPrevious,
  PaginationNext,
  PaginationList,
  PaginationPage,
  PaginationGap,
} from "../pagination";

interface DataTablePaginationProps {
  // Pagination state
  currentPage: number;
  totalPages: number;
  totalItems: number;
  pageSize: number;
  pageSizeOptions: number[];

  // Event handlers
  onPageChange?: (page: number) => void;
  onPageSizeChange?: (size: number) => void;

  // Styling
  className?: string;
}

export function DataTablePagination({
  currentPage,
  totalPages,
  totalItems,
  pageSize,
  pageSizeOptions,
  onPageChange,
  onPageSizeChange,
  className,
}: DataTablePaginationProps) {
  const renderPaginationPages = () => {
    const pages = [];

    if (totalPages <= 7) {
      // Show all pages if 7 or fewer
      for (let i = 1; i <= totalPages; i++) {
        pages.push(
          <PaginationPage
            key={i}
            current={i === currentPage}
            onClick={() => onPageChange?.(i)}
          >
            {i}
          </PaginationPage>
        );
      }
    } else {
      // Dynamic pagination that ensures current page is visible
      if (currentPage <= 3) {
        // Near start: show first 3, dots, last 3
        for (let i = 1; i <= 3; i++) {
          pages.push(
            <PaginationPage
              key={i}
              current={i === currentPage}
              onClick={() => onPageChange?.(i)}
            >
              {i}
            </PaginationPage>
          );
        }
        pages.push(<PaginationGap key="gap" />);
        for (let i = totalPages - 2; i <= totalPages; i++) {
          pages.push(
            <PaginationPage
              key={i}
              current={i === currentPage}
              onClick={() => onPageChange?.(i)}
            >
              {i}
            </PaginationPage>
          );
        }
      } else if (currentPage >= totalPages - 2) {
        // Near end: show first 3, dots, last 3
        for (let i = 1; i <= 3; i++) {
          pages.push(
            <PaginationPage
              key={i}
              current={i === currentPage}
              onClick={() => onPageChange?.(i)}
            >
              {i}
            </PaginationPage>
          );
        }
        pages.push(<PaginationGap key="gap" />);
        for (let i = totalPages - 2; i <= totalPages; i++) {
          pages.push(
            <PaginationPage
              key={i}
              current={i === currentPage}
              onClick={() => onPageChange?.(i)}
            >
              {i}
            </PaginationPage>
          );
        }
      } else {
        // In middle: show first page, dots, current area, dots, last page
        pages.push(
          <PaginationPage
            key={1}
            current={1 === currentPage}
            onClick={() => onPageChange?.(1)}
          >
            1
          </PaginationPage>
        );
        pages.push(<PaginationGap key="gap1" />);

        // Show current page ± 1
        for (let i = currentPage - 1; i <= currentPage + 1; i++) {
          pages.push(
            <PaginationPage
              key={i}
              current={i === currentPage}
              onClick={() => onPageChange?.(i)}
            >
              {i}
            </PaginationPage>
          );
        }

        pages.push(<PaginationGap key="gap2" />);
        pages.push(
          <PaginationPage
            key={totalPages}
            current={totalPages === currentPage}
            onClick={() => onPageChange?.(totalPages)}
          >
            {totalPages}
          </PaginationPage>
        );
      }
    }

    return pages;
  };

  return (
    <div
      className={`flex items-center justify-between px-4 py-3 border-t border-gray-200 ${
        className || ""
      }`}
    >
      <div className="flex items-center gap-2 text-sm text-gray-700">
        <span>Showing</span>
        <div className="inline-block w-25">
          <Select
            value={String(pageSize)}
            selectMenuPosition={"bottom-full"}
            onChange={(value) => onPageSizeChange?.(Number(value))}
            options={pageSizeOptions.map((size) => ({
              value: String(size),
              label: String(size),
            }))}
          />
        </div>
        <span className="font-medium">
          of {totalItems?.toLocaleString()} results
        </span>
      </div>

      <Pagination>
        <PaginationPrevious
          onClick={
            currentPage > 1 ? () => onPageChange?.(currentPage - 1) : undefined
          }
        />
        <PaginationList>{renderPaginationPages()}</PaginationList>
        <PaginationNext
          onClick={
            currentPage < totalPages
              ? () => onPageChange?.(currentPage + 1)
              : undefined
          }
        />
      </Pagination>
    </div>
  );
}

export default DataTablePagination;
