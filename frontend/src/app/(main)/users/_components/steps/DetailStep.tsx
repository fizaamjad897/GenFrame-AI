"use client";

import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { PhoneInput } from "@/components/ui/phone-input";
import { isValidPhoneNumber } from "libphonenumber-js";
import { Eye, EyeOff } from "lucide-react";

interface DetailStepProps {
    formData: {
        ownerName: string;
        primaryEmail: string;
        password: string;
        phone: string;
        role: string;
    };
    onChange: (field: string, value: string | File | null) => void;
    isEdit?: boolean;
}

const roles = [
    { label: "Admin", value: "admin" },
    { label: "Restricted User", value: "restricted_user" },
]

export function DetailStep({ formData, onChange, isEdit }: DetailStepProps) {
    const [emailError, setEmailError] = useState("");
    const [emailTouched, setEmailTouched] = useState(false);
    const [phoneError, setPhoneError] = useState("");
    const [phoneTouched, setPhoneTouched] = useState(false);
    const [showPassword, setShowPassword] = useState(false);


    const validateEmail = (email: string) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    };

    const handleEmailChange = (value: string) => {
        onChange("primaryEmail", value);
        if (!value || (emailTouched && validateEmail(value))) {
            setEmailError("");
        }
    };

    const handleEmailBlur = () => {
        setEmailTouched(true);
        if (formData.primaryEmail && !validateEmail(formData.primaryEmail)) {
            setEmailError("Please enter a valid email address");
        } else {
            setEmailError("");
        }
    };

    useEffect(() => {
        if (
            emailTouched &&
            formData.primaryEmail &&
            !validateEmail(formData.primaryEmail)
        ) {
            setEmailError("Please enter a valid email address");
        } else if (emailTouched) {
            setEmailError("");
        }
    }, [formData.primaryEmail, emailTouched]);

    const validatePhone = (phone: string) => {
        if (!phone) return true;
        try {
            // Ensure phone starts with exactly one +
            const formatted = phone.startsWith("+") ? phone : `+${phone}`;
            return isValidPhoneNumber(formatted);
        } catch {
            return false;
        }
    };

    const handlePhoneChange = (value: string) => {
        onChange("phone", value);
        if (phoneTouched && validatePhone(value)) {
            setPhoneError("");
        }
    };

    const handlePhoneBlur = () => {
        setPhoneTouched(true);
        if (formData.phone && !validatePhone(formData.phone)) {
            setPhoneError("Please enter a valid phone number");
        } else {
            setPhoneError("");
        }
    };

    return (
        <div className="space-y-7 pb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Owner Name
                    </label>
                    <Input
                        type="text"
                        disabled={isEdit}
                        value={formData.ownerName}
                        onChange={(e) => onChange("ownerName", e.target.value)}
                        placeholder="Enter owner name"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Primary Email
                    </label>
                    <Input
                        type="email"
                        disabled={isEdit}
                        value={formData.primaryEmail}
                        onChange={(e) => handleEmailChange(e.target.value)}
                        onBlur={handleEmailBlur}
                        placeholder="email@example.com"
                        intent={emailError ? "error" : "default"}
                    />
                    <div className="h-0 mt-0.5">
                        {emailError && (
                            <p className="text-sm mt-0.5 text-gray-400">{emailError}</p>
                        )}
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Password
                    </label>

                    <div className="relative">
                        <Input
                            type={showPassword ? "text" : "password"}
                            disabled={isEdit}
                            value={isEdit && !formData.password ? "••••••••" : formData.password}
                            onChange={(e) => onChange("password", e.target.value)}
                            placeholder="Enter password"
                        />

                        <button
                            type="button"
                            onClick={() => setShowPassword((prev) => !prev)}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-gray-500"
                        >
                            {formData.password && (showPassword ? <Eye className="w-4 h-4 text-gray-900" /> : <EyeOff className="w-4 h-4 text-gray-900" />)}
                        </button>
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Phone (optional)
                    </label>
                    <PhoneInput
                        value={formData.phone}
                        onChange={(value) => handlePhoneChange(value)}
                        onBlur={handlePhoneBlur}
                        intent={phoneError ? "error" : "default"}
                    />
                    <div className="h-0 mt-0.5">
                        {phoneError && (
                            <p className="text-sm mt-0.5 text-gray-400">{phoneError}</p>
                        )}
                    </div>
                </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Select Role
                    </label>
                    <Select
                        value={formData.role}
                        onChange={(value) => onChange("role", value)}
                        menuClassName="max-h-50"
                        options={[
                            ...roles.map((role) => ({ value: role.value, label: role.label })),
                        ]}
                    />
                </div>
            </div>
        </div>
    );
}
