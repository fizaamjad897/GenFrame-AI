"use client";

import {
  Button as HeadlessButton,
  ButtonProps as HeadlessButtonProps,
  CloseButton,
  Menu,
  MenuButton,
  MenuItems,
  MenuItem,
  Transition,
} from "@headlessui/react";
import clsx from "clsx";
import { LayoutGroup, motion } from "motion/react";
import React, { forwardRef, useId, useState } from "react";
import { usePathname } from "next/navigation";
import { TouchTarget } from "./button";
import { Link } from "./link";
import { Button } from "@/components/ui/button";
import {
  ChevronDown,
  ChevronRight,
  LogOut,
  MousePointerClick,
  Sparkles,
  Users as UsersIcon,
  CreditCard,
  Settings,
  HomeIcon,
  Archive,
  ShieldCheck,
} from "lucide-react";
import { useAuth } from "@/app/context/AuthContext";
import GridMark from "@/app/theme/GridMark";
import { CREAM, INK, ACCENT, TEXT_MUTED_L, TEXT_MUTED_D, BORDER_L, MONO } from "@/app/theme/terminal";
import { decodeJwtToken } from "@/lib/jwtUtils";
// import { sidebarRouteAccess } from "@/lib/routeAccessConfig";
const sidebarRouteAccess = (path: string, type: any, role: any) => true;
import { usePageHeader } from "@/app/context/PageHeaderContext";
// import { AIChatSidebar, useChat, type ChatMessage } from "@/components/chat";
const useChat = () => ({
  messages: [],
  sendMessage: () => {},
  isLoading: false,
});
type ChatMessage = any;
const AIChatSidebar = (props: any) => null;
import { useRouter } from "next/navigation";
// import { useGetFolderSidebarInfoQuery } from "@/graphql/apis/playerApi";
import ProgressBar from "./progress-bar";
import { Divider } from "./divider";

export function Sidebar({
  className,
  ...props
}: React.ComponentPropsWithoutRef<"nav">) {
  return (
    <nav
      {...props}
      className={clsx(className, "flex h-[100dvh] flex-col overflow-visible")}
    />
  );
}

export function SidebarHeader({
  className,
  ...props
}: React.ComponentPropsWithoutRef<"div">) {
  return (
    <div
      {...props}
      className={clsx(
        className,
        "flex flex-col shrink-0 p-4 [&>[data-slot=section]+[data-slot=section]]:mt-2.5",
      )}
    />
  );
}

export function SidebarBody({
  className,
  ...props
}: React.ComponentPropsWithoutRef<"div">) {
  return (
    <div
      {...props}
      className={clsx(
        className,
        "flex flex-1 min-h-0 flex-col overflow-y-auto scrollbar-subtle p-4 [&>[data-slot=section]+[data-slot=section]]:mt-8",
      )}
    />
  );
}

export function SidebarFooter({
  className,
  ...props
}: React.ComponentPropsWithoutRef<"div">) {
  return (
    <div
      {...props}
      className={clsx(
        className,
        "flex flex-col shrink-0 p-4 [&>[data-slot=section]+[data-slot=section]]:mt-2.5 md:mb-2",
      )}
    />
  );
}

export function SidebarSection({
  className,
  ...props
}: React.ComponentPropsWithoutRef<"div">) {
  let id = useId();

  return (
    <LayoutGroup id={id}>
      <div
        {...props}
        data-slot="section"
        className={clsx(className, "flex flex-col gap-0.5")}
      />
    </LayoutGroup>
  );
}

export function SidebarDivider({
  className,
  ...props
}: React.ComponentPropsWithoutRef<"hr">) {
  return (
    <hr
      {...props}
      className={clsx(className, "my-4 border-t lg:-mx-4")}
      style={{ borderColor: "var(--color-gray-200)" }}
    />
  );
}

export function SidebarSpacer({
  className,
  ...props
}: React.ComponentPropsWithoutRef<"div">) {
  return (
    <div
      aria-hidden="true"
      {...props}
      className={clsx(className, "mt-8 flex-1")}
    />
  );
}

export function SidebarHeading({
  className,
  ...props
}: React.ComponentPropsWithoutRef<"h3">) {
  return (
    <h3
      {...props}
      className={clsx(className, "mb-1 px-2 text-xs/6 font-medium")}
      style={{ color: "var(--color-gray-500)" }}
    />
  );
}

// Collapsible Sidebar Item Component
export function SidebarCollapsibleItem({
  icon,
  label,
  children,
  defaultOpen = false,
  current = false,
  className,
}: {
  icon: React.ReactNode;
  label: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
  current?: boolean;
  className?: string;
}) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  // console.log(data?.used_percentage);
  return (
    <div className={clsx(className, "space-y-1")}>
      <HeadlessButton
        onClick={() => setIsOpen(!isOpen)}
        className={clsx(
          "flex w-full items-center gap-3 rounded-lg px-2 py-2.5 text-left text-sm font-medium transition-colors",
          "hover:bg-[color:var(--color-gray-200)]",
          "dark:hover:bg-[color:var(--color-gray-200)]",
          current &&
            "bg-[color:var(--color-gray-200)] dark:bg-[color:var(--color-gray-200)]",
        )}
        style={{
          color: current ? "var(--color-gray-800)" : "var(--color-gray-600)",
        }}
      >
        <span className="flex h-5 w-5 items-center justify-center fill-current">
          {icon}
        </span>
        <span className="flex-1 truncate">{label}</span>
        <span className="transition-transform duration-200 fill-current">
          {isOpen ? (
            <ChevronDown className="h-4 w-4" />
          ) : (
            <ChevronRight className="h-4 w-4" />
          )}
        </span>
      </HeadlessButton>
      {isOpen && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="ml-8 space-y-1 overflow-hidden"
        >
          {children}
        </motion.div>
      )}
    </div>
  );
}

export function GenAiSidebarCollapsibleItem({
  icon,
  label,
  children,
  defaultOpen = false,
  current = false,
  className,
}: {
  icon: React.ReactNode;
  label: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
  current?: boolean;
  className?: string;
}) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className={clsx(className, "space-y-1")}>
      <HeadlessButton
        onClick={() => setIsOpen(!isOpen)}
        className={clsx(
          "flex w-full items-center gap-3 rounded-lg px-2 py-2.5 text-left text-sm font-medium transition-colors border border-[#BAE6FD]",
          "hover:bg-[color:var(--color-gray-200)]",
          "dark:hover:bg-[color:var(--color-gray-200)]",
          current &&
            "bg-[color:var(--color-gray-200)] dark:bg-[color:var(--color-gray-200)]",
        )}
        style={{
          color: current ? "var(--color-gray-800)" : "var(--color-gray-600)",
        }}
      >
        <span className="flex h-5 w-5 items-center justify-center fill-current">
          {icon}
        </span>
        <span className="flex-1 truncate text-primary">{label}</span>
        <span className="transition-transform duration-200 fill-current">
          {isOpen ? (
            <ChevronDown className="h-4 w-4 text-primary" />
          ) : (
            <ChevronRight className="h-4 w-4 text-primary" />
          )}
        </span>
      </HeadlessButton>
      {isOpen && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="ml-8 space-y-1 overflow-hidden"
        >
          {children}
        </motion.div>
      )}
    </div>
  );
}

export const SidebarItem = forwardRef(function SidebarItem(
  {
    current,
    className,
    children,
    ...props
  }: { current?: boolean; className?: string; children: React.ReactNode } & (
    | ({ href?: never } & Omit<HeadlessButtonProps, "as" | "className">)
    | ({ href: string } & Omit<
        HeadlessButtonProps<typeof Link>,
        "as" | "className"
      >)
  ),
  ref: React.ForwardedRef<HTMLAnchorElement | HTMLButtonElement>,
) {
  let classes = clsx(
    // Base
    "flex w-full items-center gap-3 rounded-lg px-2 py-2.5 text-left text-base/6 font-medium sm:py-2 sm:text-sm/5",
    // Leading icon/icon-only
    "*:data-[slot=icon]:size-6 *:data-[slot=icon]:shrink-0 *:data-[slot=icon]:fill-current sm:*:data-[slot=icon]:size-5",
    // Trailing icon (down chevron or similar)
    "*:last:data-[slot=icon]:ml-auto *:last:data-[slot=icon]:size-5 sm:*:last:data-[slot=icon]:size-4",
    // Avatar
    "*:data-[slot=avatar]:-m-0.5 *:data-[slot=avatar]:size-7 sm:*:data-[slot=avatar]:size-6",
    // Hover - consistent gray-200 for light mode, gray-800 for dark mode
    "hover:bg-[color:var(--color-gray-200)]",
    "dark:hover:bg-[color:var(--color-gray-200)]",
    // Active
    "data-active:bg-[color:var(--color-gray-200)] data-active:*:data-[slot=icon]:fill-current",
    "dark:data-active:bg-[color:var(--color-gray-200)]",
    // Current
    "data-current:*:data-[slot=icon]:fill-current",
  );

  return (
    <span className={clsx(className, "relative")}>
      {typeof props.href === "string" ? (
        <CloseButton
          as={Link}
          {...props}
          className={clsx(
            classes,
            current &&
              "bg-[color:var(--color-gray-200)] dark:bg-[color:var(--color-gray-200)]",
          )}
          data-current={current ? "true" : undefined}
          ref={ref}
          style={{
            color: current ? "var(--color-gray-800)" : "var(--color-gray-600)",
          }}
        >
          <TouchTarget>{children}</TouchTarget>
        </CloseButton>
      ) : (
        <HeadlessButton
          {...props}
          className={clsx(
            "cursor-default",
            classes,
            current &&
              "bg-[color:var(--color-gray-200)] dark:bg-[color:var(--color-gray-200)]",
          )}
          data-current={current ? "true" : undefined}
          ref={ref}
          style={{
            color: current ? "var(--color-gray-800)" : "var(--color-gray-600)",
          }}
        >
          <TouchTarget>{children}</TouchTarget>
        </HeadlessButton>
      )}
    </span>
  );
});

export function SidebarLabel({
  className,
  ...props
}: React.ComponentPropsWithoutRef<"span">) {
  return <span {...props} className={clsx(className, "truncate")} />;
}

// SignageX Sidebar Component - Matches Figma Design
export function SignageXSidebar({
  className,
  position = "left",
  fixed = false,
  folderInfo,
  folderInfoLoading,
  onCollapse,
  onRequestOrgAccess,
}: {
  className?: string;
  position?: "left" | "right";
  fixed?: boolean;
  folderInfo?: {
    used_percentage: number;
    used_players: number;
    total_players: number;
  } | null;
  folderInfoLoading?: boolean;
  onCollapse?: () => void;
  onRequestOrgAccess?: () => void;
}) {
  const [isClient, setIsClient] = React.useState(false);
  const pathname = usePathname?.() ?? "/";
  const { user, logout } = useAuth();
  const isPostpaid = Boolean(user?.is_postpaid);
  const availableEngines =
    user?.available_engines && user.available_engines.length > 0
      ? user.available_engines
      : ["transformation", "creation"];
  const canAccessCreation = availableEngines.includes("creation");
  const canAccessTransformation = availableEngines.includes("transformation");
  // console.log("Sidebar render - user:", user);
  const router = useRouter();

  React.useEffect(() => {
    setIsClient(true);
  }, []);

  // Decode JWT token to check impersonation status
  const token = localStorage.getItem("auth_token");
  const decodedToken = token ? decodeJwtToken(token) : null;
  const isImpersonated = decodedToken?.impersonated === true;
  const orgTypeName = String(
    decodedToken?.orgTypeName || decodedToken?.orgType || decodedToken?.org_type_name || "",
  );
  const isParentOrgType = orgTypeName === "SuperOrg" || orgTypeName === "AppOwner";
  const canManageOrganizations =
    !isImpersonated &&
    isParentOrgType;
  // Check if we're in simple/creation mode
  let isSimpleMode = false;
  try {
    const { header } = usePageHeader();
    isSimpleMode = header.simpleMode ?? false;
  } catch {
    // PageHeaderContext not available, use normal mode
  }

  // Get chat state for simple mode
  let chatState: {
    messages: ChatMessage[];
    sendMessage: (msg: string) => void;
    isLoading: boolean;
  } = {
    messages: [],
    sendMessage: () => {},
    isLoading: false,
  };
  try {
    chatState = useChat();
  } catch {
    // ChatProvider not available
  }

  // compute active flags for sidebar items (exact match or nested route)
  const orgActive =
    pathname === "/organizations" || pathname.startsWith("/organizations/");
  const dashboardActive =
    pathname === "/dashboard" || pathname.startsWith("/dashboard/");
  const billingActive =
    pathname === "/billing" || pathname.startsWith("/billing/");
  // const pricingActive =
  //   pathname === "/pricing" || pathname.startsWith("/pricing/");
  const settingsActive =
    pathname === "/settings" || pathname.startsWith("/settings/");
  const archiveActive =
    pathname === "/archive" || pathname.startsWith("/archive/");
  const reportsActive =
    pathname === "/reports" || pathname.startsWith("/reports/");

  let base = "w-64";
  let placement = fixed
    ? position === "left"
      ? "fixed inset-y-0 left-0"
      : "fixed inset-y-0 right-0"
    : "";
  let orderClass = fixed ? "" : position === "right" ? "order-2" : "order-1";

  let containerClass = clsx(placement, base, orderClass);

  // If in simple mode, render AI Chat sidebar
  if (isSimpleMode) {
    return (
      <Sidebar
        className={clsx(className, containerClass)}
        style={{
          background: "white",
          color: "var(--foreground)",
          borderColor: "var(--color-gray-200)",
        }}
      >
        <AIChatSidebar
          // messages={chatState.messages}
          // onSendMessage={chatState.sendMessage}
          // isLoading={chatState.isLoading}
          onCollapse={onCollapse}
        />
      </Sidebar>
    );
  }

  // Normal mode: render navigation sidebar
  return (
    <Sidebar
      className={clsx(className, containerClass)}
      style={{
        background: "var(--color-gray-100)",
        color: "var(--foreground)",
        borderColor: "var(--color-gray-200)",
      }}
    >
      <div className="flex flex-col flex-1 min-h-0">
        <SidebarHeader>
          {/* Recreative AI Logo/Brand */}
          <div
            className="flex items-center gap-2.5 px-2 py-1 cursor-pointer"
            onClick={() => {
              router.push("/dashboard");
            }}
          >
            <GridMark size={36} />
            <div>
              <div style={{ fontSize: 17, fontWeight: 600, color: INK, letterSpacing: "-0.02em" }}>
                Recreative AI
              </div>
              <div style={{ fontSize: 10, color: TEXT_MUTED_L, letterSpacing: "0.06em", textTransform: "uppercase" }}>
                AI Image Adaptation
              </div>
            </div>
          </div>
        </SidebarHeader>

        <SidebarBody>
          <SidebarSection>
            {canManageOrganizations && (
              <SidebarItem href="/organizations" current={orgActive}>
                <UsersIcon className="h-5 w-5" />
                <SidebarLabel>Organizations</SidebarLabel>
              </SidebarItem>
            )}
            <SidebarItem href="/dashboard" current={pathname === "/dashboard"}>
              <HomeIcon className="h-5 w-5" />
              <SidebarLabel>Dashboard</SidebarLabel>
            </SidebarItem>
            {/* Engines */}
            <div className="flex items-center gap-2 mt-5 mb-2 px-2">
              <span style={{ fontFamily: MONO, fontSize: 10.5, fontWeight: 600, color: ACCENT, letterSpacing: "0.08em", textTransform: "uppercase" }}>Engines</span>
              <div className="flex-1" style={{ borderTop: `1px solid ${BORDER_L}` }} />
            </div>
            {canAccessCreation && (
              <SidebarItem
                href="/creation-engine"
                current={pathname === "/creation-engine"}
              >
                <Sparkles className="h-5 w-5" />
                <SidebarLabel>Creation Engine</SidebarLabel>
              </SidebarItem>
            )}
            {canAccessTransformation && (
              <SidebarItem
                href="/transformation-engine"
                current={pathname === "/transformation-engine"}
              >
                <MousePointerClick className="h-5 w-5" />
                <SidebarLabel>Transformation Engine</SidebarLabel>
              </SidebarItem>
            )}
            <div className="flex items-center gap-2 mt-5 mb-2 px-2">
              <span style={{ fontFamily: MONO, fontSize: 10.5, fontWeight: 600, color: TEXT_MUTED_L, letterSpacing: "0.08em", textTransform: "uppercase" }}>
                Administration
              </span>
              <div className="flex-1" style={{ borderTop: `1px solid ${BORDER_L}` }} />
            </div>
            {/* Billing */}
            <SidebarItem href="/billing" current={billingActive}>
              <CreditCard className="h-5 w-5" />
              <SidebarLabel>Billing</SidebarLabel>
            </SidebarItem>
            {/* Archive */}
            <SidebarItem href="/archive" current={archiveActive}>
              <Archive className="h-5 w-5" />
              <SidebarLabel>Archive</SidebarLabel>
            </SidebarItem>
            {/* Compliance Reports */}
            <SidebarItem href="/reports" current={reportsActive}>
              <ShieldCheck className="h-5 w-5" />
              <SidebarLabel>Compliance Reports</SidebarLabel>
            </SidebarItem>
            {/* Settings */}
            <SidebarItem href="/settings" current={settingsActive}>
              <Settings className="h-5 w-5" />
              <SidebarLabel>Settings</SidebarLabel>
            </SidebarItem>
          </SidebarSection>
        </SidebarBody>
      </div>

      <SidebarFooter
        className="w-full p-4 flex flex-col justify-end gap-4"
        style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
      >
        {/* Credit Usage Display */}
        {!isSimpleMode && folderInfo && !isPostpaid && (
          <div>
            <div
              className="rounded-lg pb-4 pt-2 px-2 shadow-md relative overflow-hidden"
              style={{
                background: INK,
                border: `1px solid ${BORDER_L}`,
                color: CREAM,
              }}
            >
              <div className="relative flex justify-center mb-2">
                <svg
                  className="h-20 w-20 transform -rotate-90"
                  viewBox="0 0 100 100"
                >
                  {/* Background ring */}
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    stroke="rgba(244,239,230,0.18)"
                    strokeWidth="8"
                    fill="transparent"
                  />

                  {/* Progress ring */}
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    stroke={ACCENT}
                    strokeWidth="8"
                    fill="transparent"
                    strokeDasharray={251.32} // 2 * PI * 40
                    strokeDashoffset={
                      251.32 -
                      (Math.min(folderInfo.used_percentage, 100) / 100) * 251.32
                    }
                    strokeLinecap="round"
                    className="transition-all duration-700 ease-out"
                  />

                  {/* Percentage */}
                  <text
                    x="50"
                    y="50"
                    textAnchor="middle"
                    dominantBaseline="central"
                    fill={CREAM}
                    fontSize="14"
                    fontWeight={700}
                    transform="rotate(90 50 50)"
                  >
                    {Math.round(folderInfo.used_percentage)}%
                  </text>
                </svg>
              </div>

              <div className="text-sm font-bold tracking-wide">
                Credit Usage
              </div>
              <p
                className="text-[11px] leading-relaxed"
                style={{ color: TEXT_MUTED_D }}
              >
                You're using {folderInfo.used_players.toLocaleString()} of your{" "}
                {folderInfo.total_players.toLocaleString()} available credits.
                {folderInfo.used_percentage >= 90
                  ? "Running low? Top up now."
                  : "You're all set!"}
              </p>
            </div>
          </div>
        )}
        <Menu as="div" className=" w-full">
          <div>
            <MenuButton
              className="w-full rounded-md bg-[color:var(--color-gray-200)] p-3 flex items-center gap-3 border"
              style={{
                borderColor: "var(--color-gray-200)",
                background: "var(--color-gray-200)",
              }}
            >
              {isClient && user?.avatar ? (
                <img
                  src={user.avatar}
                  alt={user?.fullName || "User Avatar"}
                  className="h-10 w-10 rounded-md object-contain"
                />
              ) : (
                <GridMark size={40} />
              )}

              <div className="flex-1 text-left">
                <div className="flex items-center justify-between">
                  <div className="flex flex-col gap-0">
                    <div
                      className="text-sm font-semibold  max-w-[130px] line-clamp-1"
                      style={{ color: "var(--foreground)" }}
                    >
                      {isClient ? user?.fullName || "Unknown User" : "User"}
                    </div>
                    <div
                      className="text-xs truncate max-w-[130px] line-clamp-1"
                      style={{ color: "var(--color-gray-500)" }}
                      title={isClient ? user?.email || "" : ""}
                    >
                      {isClient ? user?.email || "No email" : "Loading…"}
                    </div>
                  </div>

                  <ChevronRight
                    className="h-5 w-5 transform rotate-90 text-[color:var(--color-gray-500)]"
                    aria-hidden="true"
                  />
                </div>
              </div>
            </MenuButton>
          </div>

          <Transition
            as={React.Fragment}
            enter="transition ease-out duration-100"
            enterFrom="transform opacity-0 scale-95"
            enterTo="transform opacity-100 scale-100"
            leave="transition ease-in duration-75"
            leaveFrom="transform opacity-100 scale-100"
            leaveTo="transform opacity-0 scale-95"
          >
            <MenuItems
              className="absolute bottom-14 left-0 w-full origin-bottom focus:outline-none z-50"
              style={{ background: CREAM, border: `1px solid ${BORDER_L}`, borderRadius: 3, boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)" }}
            >
              <div className="px-1 py-1">
                <MenuItem>
                  {({ focus }) => (
                    <button
                      onClick={() => {
                        logout();
                        router.push("/");
                      }}
                      className="group flex w-full items-center px-4 py-2 text-sm"
                      style={{ background: focus ? "var(--color-gray-200)" : "transparent", color: INK, borderRadius: 2 }}
                    >
                      <LogOut className="mr-2 h-4 w-4" />
                      Sign out
                    </button>
                  )}
                </MenuItem>
              </div>
            </MenuItems>
          </Transition>
        </Menu>
      </SidebarFooter>
    </Sidebar>
  );
}
