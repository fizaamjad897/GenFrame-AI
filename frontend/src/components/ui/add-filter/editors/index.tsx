"use client";

import dynamic from "next/dynamic";
import type React from "react";

export interface EditorProps {
  onCancel: () => void;
  onSave: (payload: { condition: string; value?: string }) => void;
  initialCondition?: string;
  initialValue?: string;
}

export type EditorComponent = React.ComponentType<EditorProps>;

// Dynamically import editors so the main panel doesn't grow and editors are code-split.
export const editors: Record<string, EditorComponent> = {
  // Org Name
  "org-name": dynamic(() => import("../OrgNameFilter"), {
    ssr: false,
  }) as unknown as EditorComponent,
  // Status
  status: dynamic(() => import("../StatusFilter"), {
    ssr: false,
  }) as unknown as EditorComponent,
  // Licence Usage (Legacy)
  "licence-usage": dynamic(() => import("../LicenceUsageFilter"), {
    ssr: false,
  }) as unknown as EditorComponent,
  // Credits Usage (New alias)
  "credits-usage": dynamic(() => import("../LicenceUsageFilter"), {
    ssr: false,
  }) as unknown as EditorComponent,
  // Players Online
  "players-online": dynamic(() => import("../PlayersOnlineFilter"), {
    ssr: false,
  }) as unknown as EditorComponent,
  // Created
  created: dynamic(() => import("../CreatedFilter"), {
    ssr: false,
  }) as unknown as EditorComponent,
  // Next Charge
  "next-charge": dynamic(() => import("../NextChargeFilter"), {
    ssr: false,
  }) as unknown as EditorComponent,
  // Player name editor
  "player-name": dynamic(() => import("../PlayerNameFilter"), {
    ssr: false,
  }) as unknown as EditorComponent,
  // Error editor
  errors: dynamic(() => import("../ErrorFilter"), {
    ssr: false,
  }) as unknown as EditorComponent,
  // Warning editor
  warnings: dynamic(() => import("../WarningFilter"), {
    ssr: false,
  }) as unknown as EditorComponent,
  // Tags editor
  tags: dynamic(() => import("../TagsFilter"), {
    ssr: false,
  }) as unknown as EditorComponent,
  // Connectivity editor
  connectivity: dynamic(() => import("../ConnectivityFilter"), {
    ssr: false,
  }) as unknown as EditorComponent,
  // Sync editor
  sync: dynamic(() => import("../SyncFilter"), {
    ssr: false,
  }) as unknown as EditorComponent,
  // Tags from group editor
  "tags-groups": dynamic(() => import("../TagsFromGroupFilter"), {
    ssr: false,
  }) as unknown as EditorComponent,
  // Groups editor
  groups: dynamic(() => import("../GroupsFilter"), {
    ssr: false,
  }) as unknown as EditorComponent,
  // Last seen editor
  "last-seen": dynamic(() => import("../LastSeenFilter"), {
    ssr: false,
  }) as unknown as EditorComponent,
  // Content change at editor
  "content-change-at": dynamic(() => import("../ContentChangeAtFilter"), {
    ssr: false,
  }) as unknown as EditorComponent,
  // Content sync at editor
  "content-sync-at": dynamic(() => import("../ContentSyncAtFilter"), {
    ssr: false,
  }) as unknown as EditorComponent,
  // App version editor
  "app-versions": dynamic(() => import("../AppVersionFilter"), {
    ssr: false,
  }) as unknown as EditorComponent,
  // OS version editor
  "os-versions": dynamic(() => import("../OsVersionFilter"), {
    ssr: false,
  }) as unknown as EditorComponent,
  // Note editor
  note: dynamic(() => import("../NotesFilter"), {
    ssr: false,
  }) as unknown as EditorComponent,
  // Maintenance editor
  "in-maintenance": dynamic(() => import("../MaintenanceFilter"), {
    ssr: false,
  }) as unknown as EditorComponent,
};

export default editors;
