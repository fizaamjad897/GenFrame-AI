"use client";

import React from "react";
import FilterEditor, { FilterEditorOption } from "./FilterEditor";

const options: FilterEditorOption[] = [
  { key: "is", label: "Online", hasValue: false },
  { key: "is-not", label: "Online non-Realtime", hasValue: false },
  { key: "empty", label: "Offline", hasValue: false },
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

export default function ConnectivityFilter({ onCancel, onSave }: Props) {
  return (
    <FilterEditor
      title="Connectivity"
      options={options}
      onCancel={onCancel}
      onSave={(p) =>
        onSave && onSave({ condition: p.condition, value: p.value })
      }
    />
  );
}
