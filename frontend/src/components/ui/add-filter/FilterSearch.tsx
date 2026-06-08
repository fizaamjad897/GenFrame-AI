"use client";

import React from "react";
import { Input } from "../input";
import { Search } from "lucide-react";

interface FilterSearchProps {
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
}

export default function FilterSearch({
  value,
  onChange,
  placeholder,
}: FilterSearchProps) {
  return (
    <div className="w-full">
      <div className="relative">
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">
          <Search className="w-4 h-4 text-gray-400" strokeWidth={3} />
        </span>
        <Input
          unstyled
          type="search"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="pl-10"
        />
      </div>
    </div>
  );
}
