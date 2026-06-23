"use client";

import * as Headless from "@headlessui/react";
import React, { useState } from "react";
import { NavbarItem } from "./navbar";
import { usePageHeader } from "@/app/context/PageHeaderContext";
import Image from "next/image";

function CloseMenuIcon() {
  return (
    <svg data-slot="icon" viewBox="0 0 20 20" aria-hidden="true">
      <path d="M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z" />
    </svg>
  );
}

function MobileSidebar({
  open,
  close,
  children,
}: React.PropsWithChildren<{ open: boolean; close: () => void }>) {
  return (
    <Headless.Dialog open={open} onClose={close} className="lg:hidden">
      <Headless.DialogBackdrop
        transition
        className="fixed inset-0 bg-black/30 transition data-closed:opacity-0 data-enter:duration-300 data-enter:ease-out data-leave:duration-200 data-leave:ease-in"
        onClick={close}
      />
      <Headless.DialogPanel
        transition
        className="fixed inset-y-0 w-64 max-w-80 p-2 transition duration-300 ease-in-out data-closed:-translate-x-full"
      >
        <div className="flex h-full flex-col rounded-lg overflow-y-auto">
          <div className="-mb-3 px-4 pt-3">
            <Headless.CloseButton as={NavbarItem} aria-label="Close navigation">
              <CloseMenuIcon />
            </Headless.CloseButton>
          </div>
          {children}
        </div>
      </Headless.DialogPanel>
    </Headless.Dialog>
  );
}

export function SidebarLayout({
  navbar,
  sidebar,
  children,
  position = "left",
  showSidebar: externalShowSidebar,
  onToggleSidebar: externalOnToggleSidebar,
  showDesktopSidebar: externalShowDesktopSidebar,
  onToggleDesktopSidebar: externalOnToggleDesktopSidebar,
}: React.PropsWithChildren<{
  navbar: React.ReactNode;
  sidebar: React.ReactNode;
  position?: "left" | "right";
  showSidebar?: boolean;
  onToggleSidebar?: () => void;
  showDesktopSidebar?: boolean;
  onToggleDesktopSidebar?: () => void;
}>) {
  let [internalShowSidebar, setInternalShowSidebar] = useState(false);
  let [internalShowDesktopSidebar, setInternalShowDesktopSidebar] =
    useState(true);

  // Check if we're in simple/creation mode
  let isSimpleMode = false;
  try {
    const { header } = usePageHeader();
    isSimpleMode = header.simpleMode ?? false;
  } catch {
    // PageHeaderContext not available
  }

  let showSidebar =
    externalShowSidebar !== undefined
      ? externalShowSidebar
      : internalShowSidebar;
  let onToggleSidebar =
    externalOnToggleSidebar || (() => setInternalShowSidebar(!showSidebar));

  let showDesktopSidebar =
    externalShowDesktopSidebar !== undefined
      ? externalShowDesktopSidebar
      : internalShowDesktopSidebar;
  let onToggleDesktopSidebar =
    externalOnToggleDesktopSidebar ||
    (() => setInternalShowDesktopSidebar(!showDesktopSidebar));

  return (
    <div className="relative isolate flex min-h-svh w-full bg-white lg:bg-gray-100 max-lg:flex-col dark:bg-gray-100">
      {/* Sidebar on desktop */}
      {showDesktopSidebar && (
        <div className="fixed inset-y-0 left-0 w-64 max-lg:hidden">
          {sidebar}
        </div>
      )}

      {/* Sidebar on mobile */}
      {showSidebar && (
        <MobileSidebar open={true} close={onToggleSidebar}>
          {sidebar}
        </MobileSidebar>
      )}

      {/* Content */}
      <main
        className={`relative flex w-full flex-1 flex-col lg:min-w-0 ${isSimpleMode ? "" : "pb-2 lg:pt-2 lg:pr-2 lg:pl-2"
          } ${position === "left" && showDesktopSidebar ? "lg:ml-64" : ""}`}
      >
        <div
          className={`grow w-full ${isSimpleMode ? "" : "lg:bg-gray-50"} ${isSimpleMode
            ? ""
            : "lg:rounded-lg lg:shadow-xs lg:ring-1 lg:ring-zinc-950/5 dark:lg:ring-white/10"
            }`}
        >
          <div className="mx-auto w-full max-w-[1600px]">{children}</div>
        </div>
      </main>
    </div>
  );
}
