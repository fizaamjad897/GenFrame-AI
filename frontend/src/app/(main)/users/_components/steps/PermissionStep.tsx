import PermissionsTab from '@/components/shared-tabs/PermissionsTab'
import React from 'react'

interface PermissionStepProps {
  role: string;
  onChange: (selected: string[]) => void;
  selectedPermissions?: string[];
}

const PermissionStep = ({ role, onChange, selectedPermissions }: PermissionStepProps) => {
  const Userdata = [
    { key: "add_players", label: "Allow user to add players" },
    { key: "create_player_groups", label: "Allow user to create player groups" },
    { key: "view_dashboard", label: "Allow user to view the dashboard" },
    { key: "upload_files", label: "Allow user to upload files" },
    { key: "create_compositions", label: "Allow user to create compositions" },
    { key: "create_apps", label: "Allow user to create apps" },
    { key: "create_playlists", label: "Allow user to create playlists" },
    { key: "create_audio_playlists", label: "Allow user to create audio playlists" },
    { key: "create_campaigns", label: "Allow user to create campaigns" },
    {
      key: "preview_editable_campaigns",
      label: "Allow user to preview campaigns they have edit access",
    },
    { key: "create_custom_layouts", label: "Allow user to create custom layouts" },
    { key: "create_data_feeds", label: "Allow user to create data feeds" },
    {
      key: "modify_triggers_interactivities",
      label: "Allow user to modify triggers and interactivities",
    },
    { key: "view_health_check", label: "Allow user to view health check" },
    {
      key: "create_geographic_regions",
      label: "Allow user to create geographic regions",
    },
    { key: "create_reports", label: "Allow user to create reports" },
    {
      key: "connect_integration_accounts",
      label:
        "Allow user to connect integration accounts (Facebook, Twitter...)",
    },
    {
      key: "view_change_plans_payment",
      label: "Allow user to view and change plans and payment",
    },
  ];

  const adminData = [{
    key: "admin",
    label: "Allow administrator to create and modify restricted user" // MATCHED BACKEND EXACTLY
  }]

  const data = role === "admin" ? adminData : Userdata;

  return (
    <div>
      <PermissionsTab
        data={data}
        userPage={true}
        role={role}
        onChange={onChange}
        initialPermissions={selectedPermissions}
      />
    </div>
  )
}

export default PermissionStep
