import clsx from "clsx";
import type React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "./button";

export function Pagination({
  "aria-label": ariaLabel = "Page navigation",
  className,
  ...props
}: React.ComponentPropsWithoutRef<"nav">) {
  return (
    <nav
      aria-label={ariaLabel}
      {...props}
      className={clsx(className, "flex items-center")}
    />
  );
}

export function PaginationPrevious({
  href = null,
  className,
  children = "Previous",
  onClick,
}: React.PropsWithChildren<{
  href?: string | null;
  className?: string;
  onClick?: () => void;
}>) {
  const isDisabled = href === null && !onClick;

  return (
    <button
      onClick={onClick}
      disabled={isDisabled}
      aria-label="Previous page"
      className={clsx(
        className,
        "p-2 text-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed border border-r-0 rounded-l-md min-w-9 h-8 flex items-center justify-center"
      )}
    >
      <ChevronLeft className="w-5 h-5 text-gray-500" />
    </button>
  );
}

export function PaginationNext({
  href = null,
  className,
  children = "Next",
  onClick,
}: React.PropsWithChildren<{
  href?: string | null;
  className?: string;
  onClick?: () => void;
}>) {
  const isDisabled = href === null && !onClick;

  return (
    <button
      onClick={onClick}
      disabled={isDisabled}
      aria-label="Next page"
      className={clsx(
        className,
        "p-2 text-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed border border-l-0 rounded-r-md min-w-9 h-8 flex items-center justify-center"
      )}
    >
      <ChevronRight className="w-5 h-5 text-gray-500" />
    </button>
  );
}

export function PaginationList({
  className,
  ...props
}: React.ComponentPropsWithoutRef<"span">) {
  return <span {...props} className={clsx(className, "flex items-center")} />;
}

export function PaginationPage({
  href,
  className,
  current = false,
  children,
  onClick,
}: React.PropsWithChildren<{
  href?: string;
  className?: string;
  current?: boolean;
  onClick?: () => void;
}>) {
  return (
    <button
      {...(href ? {} : { onClick })}
      aria-label={`Page ${children}`}
      aria-current={current ? "page" : undefined}
      className={clsx(
        className,
        "min-w-9 h-8 text-sm font-medium border transition-colors -ml-px first:ml-0",
        " rounded-none",
        current
          ? "bg-purple-25 border-purple-200 text-purple-700 z-10 relative"
          : "bg-white border-gray-300 text-gray-500 hover:bg-gray-50 relative"
      )}
    >
      {children}
    </button>
  );
}

export function PaginationGap({
  className,
  children = "...",
  ...props
}: React.ComponentPropsWithoutRef<"span">) {
  return (
    <span
      aria-hidden="true"
      {...props}
      className={clsx(
        className,
        "min-w-9 h-8 text-sm font-medium border border-gray-300 bg-white text-gray-500 -ml-px flex items-center justify-center select-none"
      )}
    >
      {children}
    </span>
  );
}
