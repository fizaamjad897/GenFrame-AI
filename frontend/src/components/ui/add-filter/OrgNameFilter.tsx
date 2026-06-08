"use client";

import React from "react";
import FilterEditor, { FilterEditorOption } from "./FilterEditor";

const options: FilterEditorOption[] = [
  { key: "contains", label: "contains", hasValue: true },
  { key: "not-contains", label: "does not contain", hasValue: true },
  { key: "start-with", label: "starts with", hasValue: true },
  { key: "ends-with", label: "ends with", hasValue: true },
  { key: "is", label: "is", hasValue: true },
  { key: "is-not", label: "is not", hasValue: true },
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

export default function OrgNameFilter({ onCancel, onSave }: Props) {
  return (
    <FilterEditor
      title="Organization Name"
      options={options}
      valuePlaceholder="Type name..."
      onCancel={onCancel}
      onSave={(p) =>
        onSave && onSave({ condition: p.condition, value: p.value })
      }
    />
  );
}
