// "use client";

// import React, {
//   createContext,
//   useContext,
//   useEffect,
//   useMemo,
//   useState,
// } from "react";
// import { useGetFolderSidebarInfoQuery } from "@/graphql/apis/playerApi";
// import { useAuth } from "@/context/AuthContext";

// type SidebarData = {
//   used_percentage: number;
//   used_players: number;
//   total_players: number;
// };

// type StoredValue = {
//   data: SidebarData;
//   ts: number;
// };

// const SidebarDataContext = createContext<{
//   folderInfo: SidebarData | null;
//   loading: boolean;
// }>({
//   folderInfo: null,
//   loading: true,
// });

// export function SidebarDataProvider({
//   children,
// }: {
//   children: React.ReactNode;
// }) {
//   const { user, token } = useAuth();

//   const storageKey = useMemo(() => {
//     if (!user?.orgId) return null;
//     return `sidebar-folder-info-v1:${user.orgId}`;
//   }, [user?.orgId]);

//   const [folderInfo, setFolderInfo] = useState<SidebarData | null>(() => {
//     if (typeof window === "undefined" || !storageKey) return null;
//     try {
//       const raw = localStorage.getItem(storageKey);
//       if (!raw) return null;
//       const parsed: StoredValue = JSON.parse(raw);
//       return parsed.data;
//     } catch {
//       return null;
//     }
//   });

//   const { data, isFetching, refetch } = useGetFolderSidebarInfoQuery(
//     undefined,
//     {
//       skip: !storageKey,
//       refetchOnMountOrArgChange: true, // refetch when args change
//       refetchOnFocus: false,
//       refetchOnReconnect: false,
//     },
//   );

//   useEffect(() => {
//     if (!data || !storageKey) return;

//     setFolderInfo(data);

//     const stored: StoredValue = { data, ts: Date.now() };
//     localStorage.setItem(storageKey, JSON.stringify(stored));
//   }, [data, storageKey]);

//   useEffect(() => {
//     if (token && storageKey) {
//       refetch();
//     }
//   }, [token, storageKey, refetch]);

//   useEffect(() => {
//     if (!storageKey) {
//       setFolderInfo(null);
//       return;
//     }

//     try {
//       const raw = localStorage.getItem(storageKey);
//       if (!raw) {
//         setFolderInfo(null);
//         return;
//       }
//       const parsed: StoredValue = JSON.parse(raw);
//       setFolderInfo(parsed.data);
//     } catch {
//       setFolderInfo(null);
//     }
//   }, [storageKey]);

//   return (
//     <SidebarDataContext.Provider
//       value={{
//         folderInfo,
//         loading: !folderInfo && isFetching,
//       }}
//     >
//       {children}
//     </SidebarDataContext.Provider>
//   );
// }

// export const useSidebarData = () => useContext(SidebarDataContext);

"use client";

import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
// import { useGetFolderSidebarInfoQuery } from "@/graphql/apis/playerApi";
import { useAuth } from "@/app/context/AuthContext";

const useGetFolderSidebarInfoQuery = (args: any, options: any) => ({
  data: null,
  isFetching: false,
  refetch: () => { },
});

type SidebarData = {
  used_percentage: number;
  used_players: number;
  total_players: number;
};

type StoredValue = {
  data: SidebarData;
  ts: number;
};

type SidebarContextType = {
  folderInfo: SidebarData | null;
  loading: boolean;
  collapsed: boolean;
  toggleSidebar: () => void;
  setCollapsed: (val: boolean) => void;
};

const SidebarDataContext = createContext<SidebarContextType>({
  folderInfo: null,
  loading: true,
  collapsed: false,
  toggleSidebar: () => { },
  setCollapsed: () => { },
});

export function SidebarDataProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user } = useAuth();
  const token = typeof window !== "undefined" ? localStorage.getItem("auth_token") : null;

  const [collapsed, setCollapsed] = useState<boolean>(() => {
    if (typeof window === "undefined") return false;
    const stored = localStorage.getItem("sidebar-collapsed");
    return stored === "true";
  });

  const toggleSidebar = () => {
    setCollapsed((prev) => {
      const newVal = !prev;
      localStorage.setItem("sidebar-collapsed", String(newVal));
      return newVal;
    });
  };

  const folderInfo = useMemo(() => {
    if (!user) return null;

    const engineType = (user as any).engineType || 'transformation';
    const engineInfo = (user as any).engine_data?.[engineType];
    const engineCredits = engineInfo?.credits || (user as any).credits;

    if (!engineCredits) return { used_percentage: 0, used_players: 0, total_players: 0 };

    const totalUsed = (engineCredits.monthly_units_used || 0) + (engineCredits.addon_units_used || 0);
    const totalMax = (engineCredits.monthly_units_max || 0) + (engineCredits.addon_units_max || 0);
    const used_percentage = totalMax > 0 ? (totalUsed / totalMax) * 100 : 0;

    return {
      used_percentage,
      used_players: totalUsed,
      total_players: totalMax
    };
  }, [user]);

  const loading = false;

  return (
    <SidebarDataContext.Provider
      value={{
        folderInfo,
        loading,
        collapsed,
        toggleSidebar,
        setCollapsed,
      }}
    >
      {children}
    </SidebarDataContext.Provider>
  );
}

export const useSidebarData = () => useContext(SidebarDataContext);
