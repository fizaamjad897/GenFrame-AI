"use client";

import React, { useState } from "react";
import FilterListItem from "./FilterListItem";
import { FilterItem } from "./AddFilterPanel";

interface FilterListProps {
  items: FilterItem[];
  onOpenEditor?: (id: string) => void;
}

export default function FilterList({ items, onOpenEditor }: FilterListProps) {
  const [openId, setOpenId] = useState<string | null>(null);

  const handleToggle = (id: string) => {
    setOpenId(openId === id ? null : id);
  };

  if (!items.length)
    return <div className="text-sm text-muted-foreground">No results</div>;

  return (
    <div className="divide-y divide-gray-200 mx-4">
      {items.map((it) => (
        <FilterListItem
          key={it.id}
          item={it}
          isOpen={openId === it.id}
          onToggle={() => handleToggle(it.id)}
          onOpenEditor={() => onOpenEditor && onOpenEditor(it.id)}
        />
      ))}
    </div>
  );
}
