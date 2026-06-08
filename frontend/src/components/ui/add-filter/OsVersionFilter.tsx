"use client";

import React from "react";
import FilterEditor, { FilterEditorOption } from "./FilterEditor";

const options: FilterEditorOption[] = [
  { key: "is", label: "Is", hasValue: true },
  { key: "is-not", label: "Is not", hasValue: true },
  { key: "start-with", label: "Start with", hasValue: true },
  { key: "not-start-with", label: "Does not start with", hasValue: true },
  { key: "ends-with", label: "Ends with", hasValue: true },
  { key: "not-ends-with", label: "Does not end with", hasValue: true },
  { key: "contains", label: "Contains", hasValue: true },
  { key: "not-contains", label: "Does not contain", hasValue: true },
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

export default function OsVersionFilter({ onCancel, onSave }: Props) {
  const defaultValueOptions = {
    is: [
      "Windows 10",
      "Windows 11",
      "macOS 12 Monterey",
      "macOS 13 Ventura",
      "macOS 14 Sonoma",
      "Ubuntu 20.04",
      "Ubuntu 22.04",
      "Android 12",
      "Android 13",
      "iOS 15",
      "iOS 16",
      "iOS 17",
    ],
  };

  return (
    <FilterEditor
      title="OS version"
      options={options}
      defaultValueOptions={defaultValueOptions}
      valuePlaceholder="Select or type an OS version"
      onCancel={onCancel}
      onSave={(p) =>
        onSave && onSave({ condition: p.condition, value: p.value })
      }
      initialCondition={undefined}
    />
  );
}
