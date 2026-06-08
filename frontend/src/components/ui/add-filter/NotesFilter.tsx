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

export default function NotesFilter({ onCancel, onSave }: Props) {
  const defaultValueOptions = {
    is: [
      "Maintenance required",
      "Out of service",
      "Under warranty",
      "Beta testing",
      "Production ready",
      "Needs update",
      "Hardware issue",
      "Software issue",
      "Network problem",
      "User reported issue",
    ],
  };

  return (
    <FilterEditor
      title="Notes"
      options={options}
      defaultValueOptions={defaultValueOptions}
      valuePlaceholder="Select or type a note"
      onCancel={onCancel}
      onSave={(p) =>
        onSave && onSave({ condition: p.condition, value: p.value })
      }
      initialCondition={undefined}
    />
  );
}
