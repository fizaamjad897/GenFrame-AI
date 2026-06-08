"use client";
import React, { useEffect, useState } from "react";
import { Switch } from "@/components/ui/switch";

interface PlayerDetails {
  id?: string;
  name?: string;
}

interface EntityDetails {
  id?: string;
  name?: string;
}
interface Props {
  player?: PlayerDetails | null;
  group?: EntityDetails | null;
  data?: any[];
  userPage?: boolean;
  role?: string;
  onChange?: (selected: string[]) => void;
  initialPermissions?: string[];
}

export default function PermissionsTab({ player, group, data, userPage, role, onChange, initialPermissions }: Props) {
  const entity = player || group;
  const entityType = player ? "player" : "group";
  const entityLabel = entityType === "group" ? "Group" : "Player";

  const users = [
    {
      id: "u1",
      name: entityLabel,
      role: "Admin Users from Message Point Media",
    },
  ];

  const createUser = [{
    id: "u2",
    name: role === "restricted_user" ? "Restricted User Permissions" : "Admin Permissions",
    role: role === "restricted_user" ? "Permissions granted to users through groups cannot be removed individually." : "",
  }]

  const initialUsers = userPage ? createUser : users;
  const firstUserId = initialUsers[0].id;


  const [perms, setPerms] = useState<Record<string, Record<string, boolean>>>(() =>
    initialUsers.reduce((acc, u) => {
      acc[u.id] = data?.reduce((pAcc, perm) => {
        // Check if this permission LABEL is in initialPermissions
        const isInitiallySelected = initialPermissions?.includes(perm.label) || false;
        pAcc[perm.key] = isInitiallySelected;
        return pAcc;
      }, {} as Record<string, boolean>) || {};
      return acc;
    }, {} as Record<string, Record<string, boolean>>)
  );

  useEffect(() => {
    if (initialPermissions) {
      setPerms((prev) => {
        const currentSelected = data
          ?.filter((perm) => prev[firstUserId]?.[perm.key])
          .map((perm) => perm.label) || [];

        const currentSorted = [...currentSelected].sort();
        const initialSorted = [...initialPermissions].sort();

        if (JSON.stringify(currentSorted) === JSON.stringify(initialSorted)) {
          return prev;
        }

        return {
          ...prev,
          [firstUserId]: data?.reduce((acc, perm) => {
            acc[perm.key] = initialPermissions.includes(perm.label);
            return acc;
          }, {} as Record<string, boolean>) || {},
        };
      });
    }
  }, [initialPermissions, data, firstUserId]);

  useEffect(() => {
    if (!onChange || !firstUserId) return;

    const selectedPermissions = data
      ?.filter((perm) => perms[firstUserId]?.[perm.key])
      .map((perm) => perm.label) || [];

    onChange(selectedPermissions);
  }, [perms, onChange, firstUserId]);



  const toggle = (userId: string, key: string) => {
    setPerms((p: any) => ({
      ...p,
      [userId]: { ...p[userId], [key]: !p[userId][key] },
    }));
  };

  return (
    <div className="space-y-6">
      <div>
        {!userPage && (
          <h2 className="text-heading-h2 font-semibold text-gray-900 mb-4">
            Permissions
          </h2>
        )}
      </div>

      <div className="w-full sm:w-1/2 bg-gray-50 border border-gray-200 rounded-lg p-4 relative">
        {(userPage ? createUser : users).map((u) => (
          <div key={u.id}>
            {/* Header */}
            <div className="pr-6">
              <h4 className="text-subhead font-semibold text-gray-900">
                {u.name}
              </h4>
              <p className="text-body text-gray-700 mt-1">{u.role}</p>
            </div>

            <div className="mt-6 divide-y divide-gray-100">
              {data?.map((perm) => (
                <div
                  key={perm.key}
                  className="flex items-center justify-between py-2"
                >
                  <div>
                    <div className="text-subhead text-gray-900">
                      {perm.label}
                    </div>
                  </div>

                  <div>
                    <Switch
                      checked={!!perms[u.id]?.[perm.key]}
                      onChange={() => toggle(u.id, perm.key)}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
