"use client";

import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { PhoneInput } from "@/components/ui/phone-input";
import { validateEmail, getEmailValidationError } from "@/lib/validationUtils";

import { isValidPhoneNumber } from "libphonenumber-js";

interface DetailStepProps {
  formData: {
    organizationName: string;
    primaryEmail: string;
    phone: string;
    region: string;
    timeZone: string;
    industry: string;
  };
  onChange: (field: string, value: string) => void;
  isEdit?: boolean;
}

const regions = [
  "US-East",
  "US-West",
  "Europe",
  "Asia-Pacific",
  "South America",
  "Africa",
  "Middle East",
];

const timeZones = [
  "UTC-12:00",
  "UTC-11:00",
  "UTC-10:00",
  "UTC-09:30",
  "UTC-09:00",
  "UTC-08:00",
  "UTC-07:00",
  "UTC-06:00",
  "UTC-05:00",
  "UTC-04:00",
  "UTC-03:30",
  "UTC-03:00",
  "UTC-02:00",
  "UTC-01:00",
  "UTC+00:00",
  "UTC+01:00",
  "UTC+02:00",
  "UTC+03:00",
  "UTC+03:30",
  "UTC+04:00",
  "UTC+04:30",
  "UTC+05:00",
  "UTC+05:30",
  "UTC+05:45",
  "UTC+06:00",
  "UTC+06:30",
  "UTC+07:00",
  "UTC+08:00",
  "UTC+08:45",
  "UTC+09:00",
  "UTC+09:30",
  "UTC+10:00",
  "UTC+10:30",
  "UTC+11:00",
  "UTC+12:00",
  "UTC+12:45",
  "UTC+13:00",
  "UTC+14:00",
];

const industries = [
  "Retail",
  "Transit",
  "Education",
  "Hospitality",
  "Healthcare",
  "Corporate",
  "Entertainment",
  "Government",
];

export function DetailStep({ formData, onChange, isEdit }: DetailStepProps) {
  const [emailError, setEmailError] = useState("");
  const [emailTouched, setEmailTouched] = useState(false);
  const [phoneError, setPhoneError] = useState("");
  const [phoneTouched, setPhoneTouched] = useState(false);
  const [userCountry, setUserCountry] = useState("");
  const [isDetectingCountry, setIsDetectingCountry] = useState(true);

  // Detect user's country from timezone or use geolocation API with CORS
  useEffect(() => {
    const detectCountry = async () => {
      setIsDetectingCountry(true);
      try {
        // Try geolocation API with CORS support
        const response = await fetch(
          "https://geolocation-db.com/json/geoip/me",
        );
        const data = await response.json();
        if (data.country_code) {
          setUserCountry(data.country_code.toLowerCase());
        } else {
          throw new Error("No country code in response");
        }
      } catch (error) {
        console.error(
          "Failed to detect country from geolocation API, using timezone:",
          error,
        );
        // Fallback: Try to detect from timezone
        try {
          const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
          // Simple timezone to country mapping for common timezones
          const tzToCountry: { [key: string]: string } = {
            "America/New_York": "us",
            "America/Chicago": "us",
            "America/Denver": "us",
            "America/Los_Angeles": "us",
            "Europe/London": "gb",
            "Europe/Paris": "fr",
            "Europe/Berlin": "de",
            "Europe/Madrid": "es",
            "Asia/Tokyo": "jp",
            "Asia/Shanghai": "cn",
            "Asia/Hong_Kong": "hk",
            "Asia/Singapore": "sg",
            "Asia/Bangkok": "th",
            "Asia/Dubai": "ae",
            "Asia/Kolkata": "in",
            "Australia/Sydney": "au",
            "Pacific/Auckland": "nz",
          };
          const country = tzToCountry[timeZone] || "us";
          setUserCountry(country);
        } catch (tzError) {
          console.error("Failed to detect country from timezone:", tzError);
          setUserCountry("us");
        }
      } finally {
        setIsDetectingCountry(false);
      }
    };

    detectCountry();
  }, []);

  const handleEmailChange = (value: string) => {
    onChange("primaryEmail", value);
    if (!value || (emailTouched && validateEmail(value))) {
      setEmailError("");
    }
  };

  const handleEmailBlur = () => {
    setEmailTouched(true);
    if (formData.primaryEmail) {
      const error = getEmailValidationError(formData.primaryEmail);
      setEmailError(error || "");
    } else {
      setEmailError("");
    }
  };

  useEffect(() => {
    if (emailTouched && formData.primaryEmail) {
      const error = getEmailValidationError(formData.primaryEmail);
      setEmailError(error || "");
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
      {/* Row 1: Organization Name and Primary Email */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Organization Name
          </label>
          <Input
            type="text"
            value={formData.organizationName}
            onChange={(e) => onChange("organizationName", e.target.value)}
            placeholder="Enter organization name"
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
          <div className="min-h-6 mt-1">
            {emailError && <p className="text-sm text-red-500">{emailError}</p>}
          </div>
        </div>
      </div>

      {/* Row 2: Phone and Region */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Phone (optional)
          </label>
          <PhoneInput
            value={formData.phone}
            onChange={(value) => handlePhoneChange(value)}
            onBlur={handlePhoneBlur}
            defaultCountry={userCountry}
            isLoading={isDetectingCountry}
            intent={phoneError ? "error" : "default"}
          />
          <div className="min-h-6 mt-1">
            {phoneError && <p className="text-sm text-red-500">{phoneError}</p>}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Region
          </label>
          <Select
            value={formData.region}
            onChange={(value) => onChange("region", value)}
            options={[
              { value: "", label: "Select region" },
              ...regions.map((region) => ({ value: region, label: region })),
            ]}
          />
        </div>
      </div>

      {/* Row 3: Time Zone and Industry */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Time Zone
          </label>
          <Select
            value={formData.timeZone}
            onChange={(value) => onChange("timeZone", value)}
            menuClassName="max-h-50"
            options={[
              { value: "", label: "Select time zone" },
              ...timeZones.map((tz) => ({ value: tz, label: tz })),
            ]}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Industry (optional)
          </label>
          <Select
            value={formData.industry}
            onChange={(value) => onChange("industry", value)}
            options={[
              { value: "", label: "Select industry" },
              ...industries.map((industry) => ({
                value: industry,
                label: industry,
              })),
            ]}
          />
        </div>
      </div>
    </div>
  );
}
