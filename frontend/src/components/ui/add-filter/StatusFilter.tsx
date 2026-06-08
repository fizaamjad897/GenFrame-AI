"use client";

import React from "react";
import FilterEditor, { FilterEditorOption } from "./FilterEditor";

const options: FilterEditorOption[] = [
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

export default function StatusFilter({ onCancel, onSave }: Props) {
  const defaultValueOptions = {
    is: ["Active", "Inactive"],
    "is-not": ["Active", "Inactive"],
  };

  return (
    <FilterEditor
      title="Status"
      options={options}
      defaultValueOptions={defaultValueOptions}
      valuePlaceholder="Select status"
      onCancel={onCancel}
      onSave={(p) =>
        onSave && onSave({ condition: p.condition, value: p.value })
      }
    />
  );
}
