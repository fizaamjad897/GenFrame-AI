"use client";

import { parsePhoneNumberWithError } from "libphonenumber-js";

interface UserDetailsProps {
    primaryEmail?: string;
    phone?: string;
    password?: string;
    role?: string;
    ownerName?: string;
}

export function UserDetails({
    ownerName,
    primaryEmail,
    phone,
    role,
    password
}: UserDetailsProps) {
    const formatPhone = (phoneStr?: string) => {
        if (!phoneStr) return "-";
        try {
            const p = phoneStr.startsWith("+") ? phoneStr : `+${phoneStr}`;
            const phoneNumber = parsePhoneNumberWithError(p);

            if (phoneNumber) {
                if (phoneNumber.countryCallingCode === '1') {
                    return `+1 ${phoneNumber.format("NATIONAL")}`;
                }
                return phoneNumber.format("INTERNATIONAL");
            }
            return phoneStr;
        } catch {
            return phoneStr;
        }
    };

    return (
        <div className="w-full max-w-3xl">
            <div className="rounded-md border-2 border-gray-100 bg-white">
                <div className="bg-gray-50 px-6 py-3 rounded-t-md border-b border-gray-100 h-12">
                    <h4 className="text-title font-semibold text-gray-900">
                        User Details
                    </h4>
                </div>

                <div className="p-4">
                    <div className="grid grid-cols-1 md:grid-cols-[auto_1fr] gap-x-32 gap-y-3 font-medium text-subhead text-gray-700">
                        <div>Owner Name:</div>
                        <div className="text-gray-900 font-regular">
                            {ownerName || "-"}
                        </div>

                        <div>Primary Email:</div>
                        <div className="text-gray-900 font-regular">
                            {primaryEmail || "-"}
                        </div>

                        <div>Password:</div>
                        <div className="text-gray-900 font-regular">{password || "••••••••"}</div>
                        <div>Phone:</div>
                        <div className="text-gray-900 font-regular">{formatPhone(phone)}</div>

                        <div>Role:</div>
                        <div className="text-gray-900 font-regular">{role === "restricted_user" ? "Restricted User" : "Admin"}</div>

                    </div>
                </div>
            </div>
        </div>
    );
}
