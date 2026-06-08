"use client";

import React from "react";
import clsx from "clsx";
import { Button } from "../ui/button";
import { Columns2, ArrowLeft } from "lucide-react";
import Image from "next/image";
import { useSidebarData } from "@/providers/SidebarDataProvider";
type HeaderProps = {
  title?: string;
  actionLabel?: string;
  onAction?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  actionDisabled?: boolean;
  secondaryActionLabel?: string;
  onSecondaryAction?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  side?: "left" | "right";
  onToggleMobileSidebar?: () => void;
  onToggleDesktopSidebar?: () => void;
  icon?: React.ReactNode;
  simpleMode?: boolean;
  onBack?: () => void;
  sidebarCollapsed?: boolean;
  showDesktopSidebar?: boolean;
};

export function Header({
  title = "",
  actionLabel,
  onAction,
  actionDisabled = false,
  secondaryActionLabel,
  onSecondaryAction,
  side = "left",
  onToggleMobileSidebar,
  onToggleDesktopSidebar,
  icon,
  simpleMode = false,
  onBack,
  sidebarCollapsed = false,
  showDesktopSidebar = false,
}: HeaderProps) {
  const { toggleSidebar, collapsed } = useSidebarData();
  const handleToggleSidebar = () => {
    toggleSidebar();
    onToggleMobileSidebar?.();
    onToggleDesktopSidebar?.();
  };

  // console.log("in HEADER", { collapsed });
  return (
    <header
      className={clsx(
        "w-full",
        simpleMode ? "bg-gray-100" : "bg-background",
        "border-b border-gray-200",
        simpleMode ? "py-3" : "pt-2",
        !simpleMode && "lg:rounded-t-lg",
      )}
    >
      <div
        className={clsx(
          "max-w-full mx-auto grid grid-cols-[1fr_auto] items-center gap-4",
          simpleMode ? "px-6" : "pb-2",
          "max-lg:py-2",
          simpleMode && sidebarCollapsed && "lg:pl-12",
        )}
      >
        <div className="flex items-center min-w-0">
          {simpleMode ? (
            <>
              {!showDesktopSidebar && (
                <button
                  onClick={() => {
                    onToggleDesktopSidebar?.();
                    toggleSidebar();
                  }}
                  className="w-8 h-8 flex items-center justify-center cursor-pointer flex-shrink-0 lg:-ml-9"
                  aria-label="Open AI Chat"
                >
                  <Image
                    src="/icons/chat.svg"
                    alt="AI Chat"
                    width={24}
                    height={24}
                  />
                </button>
              )}
              <div
                className="h-8 w-8 rounded-md flex items-center justify-center mr-2 flex-shrink-0 cursor-pointer hover:bg-gray-100"
                onClick={onBack}
              >
                <ArrowLeft className="h-5 w-5 text-foreground" />
              </div>
            </>
          ) : (
            <div
              className="h-8 w-8 rounded-md flex items-center justify-center mr-2 ml-1 flex-shrink-0 cursor-pointer"
              onClick={handleToggleSidebar}
            >
              <Columns2 className="h-5 w-5 text-foreground" />
            </div>
          )}
          {!simpleMode && (
            <div className="w-px h-3.5 bg-gray-300 mr-3 flex-shrink-0" />
          )}

          <div className="min-w-0">
            <div className="flex items-center gap-2">
              {title ? (
                <h2 className="text-heading-h2 font-semibold text-foreground truncate">
                  {title}
                </h2>
              ) : (
                <div className="h-7 w-32 bg-gray-200 rounded animate-pulse" />
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center justify-end flex-shrink-0 mr-6">
          {secondaryActionLabel ? (
            <Button
              outline
              size="sm"
              onClick={(e) => {
                onSecondaryAction?.(e);
              }}
            >
              {secondaryActionLabel}
            </Button>
          ) : null}

          {actionLabel ? (
            <Button
              color="purple"
              size="sm"
              disabled={actionDisabled}
              className={secondaryActionLabel ? "ml-3" : undefined}
              onClick={(e) => {
                onAction?.(e);
              }}
            >
              {actionLabel}
              {icon && <span>{icon}</span>}
            </Button>
          ) : null}
        </div>
      </div>
    </header>
  );
}

export default Header;
