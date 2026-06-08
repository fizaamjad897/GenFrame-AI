"use client";

import React from "react";
import FilterEditor, { FilterEditorOption } from "./FilterEditor";

const options: FilterEditorOption[] = [
  { key: "is", label: "Is", hasValue: true },
  { key: "is-not", label: "Is not", hasValue: true },
  {
    key: "is-greater-than-or-equal",
    label: "Is greater than or equal to",
    hasValue: true,
  },
  { key: "is-less-than", label: "Is less than", hasValue: true },
  {
    key: "is-less-than-or-equal",
    label: "Is less than or equal to",
    hasValue: true,
  },
  { key: "empty", label: "Is empty", hasValue: false },
  { key: "not-empty", label: "Is not empty", hasValue: false },
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

export default function WarningFilter({ onCancel, onSave }: Props) {
  const defaultValueOptions = {
    is: [
      "Low Battery",
      "High Temperature",
      "Disk Space Low",
      "Memory Usage High",
      "Network Latency",
    ],
    "is-greater-than-or-equal": ["1", "5", "10", "50", "100"],
    "is-less-than": ["1", "5", "10", "50", "100"],
    "is-less-than-or-equal": ["1", "5", "10", "50", "100"],
  };

  return (
    <FilterEditor
      title="Warning"
      options={options}
      defaultValueOptions={defaultValueOptions}
      valuePlaceholder="Select or type a new one"
      onCancel={onCancel}
      onSave={(p) =>
        onSave && onSave({ condition: p.condition, value: p.value })
      }
      initialCondition={undefined}
    />
  );
}
