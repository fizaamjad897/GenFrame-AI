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
    label: "Not items start with",
    hasValue: true,
  },
  { key: "items-ends-with", label: "Items ends with", hasValue: true },
  { key: "not-items-ends-with", label: "Not items ends with", hasValue: true },
  { key: "empty", label: "Are empty", hasValue: false },
  { key: "not-empty", label: "Are not empty", hasValue: false },
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

export default function TagsFilter({ onCancel, onSave }: Props) {
  const defaultValueOptions = {
    contains: ["production", "test", "staging", "development"],
    "overlap-with": [
      { id: "urgent", name: "urgent" },
      { id: "priority", name: "priority" },
      { id: "maintenance", name: "maintenance" },
    ],
    "items-start-with": ["prod-", "dev-", "test-"],
    "items-ends-with": ["-v1", "-v2", "-beta"],
  };

  return (
    <FilterEditor
      title="Tags"
      options={options}
      defaultValueOptions={defaultValueOptions}
      optionsTitle="Tags"
      valuePlaceholder="Select or type a new one"
      onCancel={onCancel}
      onSave={(p) =>
        onSave && onSave({ condition: p.condition, value: p.value })
      }
      initialCondition={undefined}
    />
  );
}
