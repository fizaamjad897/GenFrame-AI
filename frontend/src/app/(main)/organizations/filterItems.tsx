import { FilterItem } from "@/components/ui/add-filter/AddFilterPanel";
import { Building2, Activity, Calendar } from "lucide-react";

export const organizationFilterItems: FilterItem[] = [
  { id: "org-name", title: "Organization Name", subtitle: "starts with", icon: <Building2 size={16} /> },
  { id: "status", title: "Status", icon: <Activity size={16} /> },
  { id: "created", title: "Created", icon: <Calendar size={16} /> },
];
