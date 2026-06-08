"use client";

import React from "react";
import FilterEditor, { FilterEditorOption } from "./FilterEditor";

const options: FilterEditorOption[] = [
  { key: "is-between", label: "is between", hasValue: true },
  { key: "is-before", label: "is before", hasValue: true },
  { key: "is-after", label: "is after", hasValue: true },
  { key: "on", label: "on", hasValue: true },
  { key: "not-on", label: "not on", hasValue: true },
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

export default function CreatedFilter({ onCancel, onSave }: Props) {
  return (
    <FilterEditor
      title="Created"
      options={options}
      onCancel={onCancel}
      onSave={(p) =>
        onSave && onSave({ condition: p.condition, value: p.value })
      }
    />
  );
}
