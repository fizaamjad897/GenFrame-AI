"use client";

import React from "react";
import FilterEditor, { FilterEditorOption } from "./FilterEditor";

const options: FilterEditorOption[] = [
  { key: "is", label: "is", hasValue: true },
  { key: "is-greater-than-or-equal", label: "is >=", hasValue: true },
  { key: "is-less-than", label: "is <", hasValue: true },
  { key: "is-between", label: "is between", hasValue: true },
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

export default function PlayersOnlineFilter({ onCancel, onSave }: Props) {
  return (
    <FilterEditor
      title="Players Online"
      options={options}
      valuePlaceholder="Enter quantity"
      onCancel={onCancel}
      onSave={(p) =>
        onSave && onSave({ condition: p.condition, value: p.value })
      }
    />
  );
}
