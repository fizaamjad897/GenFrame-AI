"use client";

import React, { useState } from "react";
import { SignageXSidebar as VisualEngineSidebar } from "../../components/ui/sidebar";
import { SidebarLayout } from "../../components/ui/sidebar-layout";
import Header from "../../components/layout/Header";
import ImpersonationHeader from "../../components/layout/ImpersonationHeader";
import { PageHeaderProvider, usePageHeader } from "../context/PageHeaderContext";
import { SidebarDataProvider, useSidebarData } from "@/providers/SidebarDataProvider";
import { AuthGuard } from "@/app/components/auth/AuthGuard";
import { PageTransition } from "@/components/motion/Reveal";

export function LayoutWrapper({
    side,
    setSide,
    showSidebar,
    setShowSidebar,
    showDesktopSidebar,
    setShowDesktopSidebar,
    children,
}: {
    side: "left" | "right";
    setSide: (side: "left" | "right") => void;
    showSidebar: boolean;
    setShowSidebar: (show: boolean) => void;
    showDesktopSidebar: boolean;
    setShowDesktopSidebar: (show: boolean) => void;
    children: React.ReactNode;
}) {
    const { folderInfo, loading } = useSidebarData();
    const { header } = usePageHeader();
    const isSimpleMode = header?.simpleMode ?? false;
    const [simpleModeDesktopSidebarOpen, setSimpleModeDesktopSidebarOpen] = useState(false);

    // Determine sidebar visibility based on mode
    const finalShowDesktopSidebar = isSimpleMode
        ? (header?.isSidebarOpen ?? simpleModeDesktopSidebarOpen)
        : showDesktopSidebar;

    const handleToggleDesktopSidebar = isSimpleMode
        ? (header?.onToggleSidebar ?? (() => setSimpleModeDesktopSidebarOpen(!simpleModeDesktopSidebarOpen)))
        : () => setShowDesktopSidebar(!showDesktopSidebar);

    return (
        <SidebarLayout
            navbar={<div></div>}
            sidebar={
                <VisualEngineSidebar
                    position={side}
                    fixed={true}
                    folderInfo={folderInfo}
                    folderInfoLoading={loading}
                    onCollapse={handleToggleDesktopSidebar}
                />
            }
            position={side}
            showSidebar={showSidebar}
            onToggleSidebar={() => setShowSidebar(!showSidebar)}
            showDesktopSidebar={finalShowDesktopSidebar}
            onToggleDesktopSidebar={handleToggleDesktopSidebar}
        >
            <ImpersonationHeader />
            {isSimpleMode ? (
                <div className="bg-gray-100 min-h-screen w-full">
                    {!header.hideHeader && (
                        <Header
                            title={header.title}
                            actionLabel={header.actionLabel}
                            actionDisabled={header.actionDisabled}
                            onAction={header.onAction}
                            icon={header.icon}
                            secondaryActionLabel={header.secondaryActionLabel}
                            onSecondaryAction={header.onSecondaryAction}
                            onToggleMobileSidebar={() => setShowSidebar(!showSidebar)}
                            onToggleDesktopSidebar={handleToggleDesktopSidebar}
                            showDesktopSidebar={finalShowDesktopSidebar}
                            side={side}
                            simpleMode={isSimpleMode}
                            onBack={header.onBack}
                            sidebarCollapsed={!showDesktopSidebar}
                        />
                    )}
                    <div className="px-4 mt-4 w-full"><PageTransition>{children}</PageTransition></div>
                </div>
            ) : (
                <>
                    <div className="mb-4 flex w-full flex-col gap-2">
                        {!header.hideHeader && (
                            <Header
                                title={header.title}
                                actionLabel={header.actionLabel}
                                actionDisabled={header.actionDisabled}
                                onAction={header.onAction}
                                icon={header.icon}
                                secondaryActionLabel={header.secondaryActionLabel}
                                onSecondaryAction={header.onSecondaryAction}
                                onToggleMobileSidebar={() => setShowSidebar(!showSidebar)}
                                onToggleDesktopSidebar={handleToggleDesktopSidebar}
                                showDesktopSidebar={finalShowDesktopSidebar}
                                side={side}
                                simpleMode={isSimpleMode}
                                onBack={header.onBack}
                                sidebarCollapsed={header.sidebarCollapsed}
                            />
                        )}
                    </div>
                    <div className="px-6 w-full"><PageTransition>{children}</PageTransition></div>
                </>
            )}
        </SidebarLayout>
    );
}

export default function MainLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const [side, setSide] = useState<"left" | "right">("left");
    const [showSidebar, setShowSidebar] = useState(false);
    const [showDesktopSidebar, setShowDesktopSidebar] = useState(true);

    return (
        <AuthGuard>
            <SidebarDataProvider>
                <PageHeaderProvider>
                    <LayoutWrapper
                        side={side}
                        setSide={setSide}
                        showSidebar={showSidebar}
                        setShowSidebar={setShowSidebar}
                        showDesktopSidebar={showDesktopSidebar}
                        setShowDesktopSidebar={setShowDesktopSidebar}
                    >
                        {children}
                    </LayoutWrapper>
                </PageHeaderProvider>
            </SidebarDataProvider>
        </AuthGuard>
    );
}
