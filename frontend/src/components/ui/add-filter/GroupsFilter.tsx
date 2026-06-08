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

export default function GroupsFilter({ onCancel, onSave }: Props) {
  const defaultValueOptions: Partial<Record<any, any[]>> = {
    contains: ["Group A", "Group B", "Group C"],
    "overlap-with": [
      { id: "group-a", name: "Group A" },
      { id: "group-b", name: "Group B" },
      { id: "group-c", name: "Group C" },
    ],
    "items-start-with": ["Group"],
    "items-ends-with": ["A", "B", "C"],
  };

  return (
    <FilterEditor
      title="Groups"
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
