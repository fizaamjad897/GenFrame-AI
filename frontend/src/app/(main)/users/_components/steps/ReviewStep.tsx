"use client";
import { PermissionView } from "./PermissionView";
import { UserDetails } from "./UserDetail";

interface ReviewFormData {
    plan?: string;
    organizationName?: string;
    ownerName?: string;
    primaryEmail?: string;
    phone?: string;
    region?: string;
    timeZone?: string;
    industry?: string;
    role?: string;
    password?: string;
}
interface ReviewStepProps {
    formData: ReviewFormData;
    selectedPermissions?: string[];
}

export function ReviewStep({ formData, selectedPermissions }: ReviewStepProps) {    

    return (
        <div className="space-y-6 pb-6">
            <UserDetails
                ownerName={formData.ownerName}
                primaryEmail={formData.primaryEmail}
                phone={formData.phone}
                password={formData.password}
                role={formData.role}
            />

            <PermissionView name={formData.role} selectedPermissons={selectedPermissions} />
        </div>
    );
}
