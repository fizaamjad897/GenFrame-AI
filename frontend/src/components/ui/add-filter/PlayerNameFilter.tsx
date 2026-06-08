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

export default function PlayerNameFilter({ onCancel, onSave }: Props) {
  const defaultValueOptions = {
    is: [
      "EX 43 KV - Aberdeen - S12333",
      "M24V - B8123",
      "M24V - B8432",
      "M24V - B8134",
      "M24V - B8145",
      "EX 44 KV - London - S54321",
      "EX 45 KV - Paris - S99999",
      "EX 46 KV - Berlin - S11111",
    ],
  };

  return (
    <FilterEditor
      title="Player name"
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
