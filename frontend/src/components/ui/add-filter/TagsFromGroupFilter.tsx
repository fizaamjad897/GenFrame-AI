"use client";

import React from "react";
import FilterEditor, { FilterEditorOption } from "./FilterEditor";

const options: FilterEditorOption[] = [
  { key: "contains", label: "Contain", hasValue: true },
  { key: "not-contains", label: "Do not contain", hasValue: true },
  {
    key: "overlap-with",
    label: "Overlap with",
    hasValue: true,
    multiSelect: true,
  },
  { key: "not-overlap-with", label: "Do not overlap with", hasValue: true },
  { key: "items-start-with", label: "Items start with", hasValue: true },
  {
    key: "not-items-start-with",
    label: "not Items start with",
    hasValue: true,
  },
  { key: "items-ends-with", label: "Items ends with", hasValue: true },
  { key: "not-items-ends-with", label: "not Items ends with", hasValue: true },
  { key: "empty", label: "are empty", hasValue: false },
  { key: "not-empty", label: "are not empty", hasValue: false },
];

interface Props {
  onCancel?: () => void;
  onSave?: (payload: {
    condition: string;
    value?:
      | string
      | string[]
      | Date
      | null
      | { start: Date | null; end: Date | null };
  }) => void;
}

export default function TagsFromGroupFilter({ onCancel, onSave }: Props) {
  const defaultValueOptions: Partial<Record<any, any[]>> = {
    contains: ["ARR / DPP", "M24V - B8123", "M24V - B8145"],
    "overlap-with": [
      { id: "arr-dpp", name: "ARR / DPP" },
      { id: "m24v-b8123", name: "M24V - B8123" },
      { id: "m24v-b8145", name: "M24V - B8145" },
    ],
    "items-start-with": ["ARR", "M24V"],
    "items-ends-with": ["B8123", "B8145"],
  };

  return (
    <FilterEditor
      title="Tags from group"
      options={options}
      defaultValueOptions={defaultValueOptions}
      optionsTitle="Types"
      valuePlaceholder="Select or type a new one"
      onCancel={onCancel}
      onSave={(p) =>
        onSave && onSave({ condition: p.condition, value: p.value })
      }
      initialCondition={undefined}
    />
  );
}
