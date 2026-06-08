"use client";

import { Check } from "lucide-react";

interface PermissionViewProps {
    id?: string;
    name?: string | undefined;
    price?: number;
    description?: string;
    features?: string[] | undefined;
    selectedPermissons?: string[];
}

export function PermissionView({ name, features, selectedPermissons }: PermissionViewProps) {
    return (
        <div className="w-full max-w-3xl">
            <div className="rounded-md border-2 border-gray-100 bg-white overflow-hidden">
                <div className="bg-gray-50 px-6 py-1 h-12 flex items-center">
                    <h4 className="text-title font-semibold text-gray-900">
                        {name === "restricted_user" ? "Restricted User Permissions" : "Admin Permissions"}                    </h4>
                </div>

                <div className="p-4">
                    <div className="grid grid-cols-1 gap-4 mt-4">
                        {selectedPermissons?.map((f, idx) => (
                            <div key={`${f}-${idx}`} className="flex items-start gap-2 text-sm text-gray-500">
                                <div className="w-6 h-6 rounded-full bg-purple-25 flex items-center justify-center">
                                    <Check className="w-4 h-4 text-primary" />
                                </div>
                                <span>{f}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
