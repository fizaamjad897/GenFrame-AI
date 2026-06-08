"use client";

import React, { useState } from "react";
import clsx from "clsx";
import { RadioGroup, Radio } from "../radio";
import { Combobox, ComboboxOption } from "../combobox";
import { MultiSelectCombobox } from "../multi-select-combobox";
import { Button } from "../button";
import DateRangePicker from "../date-range-picker";

function startOfMonth(date: Date) {
  return new Date(date.getFullYear(), date.getMonth(), 1);
}

function isDateCondition(condition: ConditionKey): boolean {
  return ["is-between", "is-before", "is-after", "on", "not-on"].includes(
    condition
  );
}

export type ConditionKey =
  | "is"
  | "is-not"
  | "start-with"
  | "not-start-with"
  | "ends-with"
  | "not-ends-with"
  | "contains"
  | "not-contains"
  | "is-greater-than-or-equal"
  | "is-less-than"
  | "is-less-than-or-equal"
  | "overlap-with"
  | "not-overlap-with"
  | "items-start-with"
  | "not-items-start-with"
  | "items-ends-with"
  | "not-items-ends-with"
  | "empty"
  | "not-empty"
  | "is-between"
  | "is-before"
  | "is-after"
  | "on"
  | "not-on"
  | "Enabled"
  | "Disabled";

export interface FilterEditorOption {
  key: ConditionKey;
  label: string;
  hasValue?: boolean;
  multiSelect?: boolean;
}

interface FilterEditorProps {
  title?: string;
  subtitle?: string;
  options: FilterEditorOption[];
  valueOptions?: Record<ConditionKey, string[]>;
  defaultValueOptions?: Partial<Record<ConditionKey, any[]>>;
  valuePlaceholder?: string;
  optionsTitle?: string;
  onCancel?: () => void;
  onSave?: (payload: {
    condition: ConditionKey;
    value?:
      | string
      | string[]
      | Date
      | null
      | { start: Date | null; end: Date | null };
  }) => void;
  initialCondition?: ConditionKey;
  initialValue?: string;
}

export default function FilterEditor({
  title,
  subtitle,
  options,
  valueOptions,
  defaultValueOptions,
  valuePlaceholder = "Select or type a new one",
  optionsTitle = "Types",
  onCancel,
  onSave,
  initialCondition,
  initialValue,
}: FilterEditorProps) {
  const [condition, setCondition] = useState<ConditionKey | "">(
    initialCondition || ""
  );
  const [singleValue, setSingleValue] = useState(initialValue || "");
  const [multiValues, setMultiValues] = useState<any[]>([]);
  const [viewMonth, setViewMonth] = useState<Date>(startOfMonth(new Date()));
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);

  const handleSave = () => {
    if (!condition) return;
    const selectedOption = options.find((opt) => opt.key === condition);
    let value:
      | string
      | string[]
      | Date
      | null
      | { start: Date | null; end: Date | null }
      | undefined;
    if (selectedOption?.multiSelect) {
      value = multiValues;
    } else if (isDateCondition(condition)) {
      value =
        condition === "is-between"
          ? { start: startDate, end: endDate }
          : startDate;
    } else {
      value = singleValue || undefined;
    }
    onSave && onSave({ condition, value });
  };

  return (
    <div className="h-full flex flex-col">
      <div className="flex-1 overflow-y-auto px-4 py-2 min-h-0">
        <RadioGroup
          value={condition}
          onChange={(v) => {
            setCondition(v as ConditionKey);
            setSingleValue("");
            setMultiValues([]);
            setStartDate(null);
            setEndDate(null);
          }}
          className="rounded-lg"
        >
          {options.map((opt) => (
            <label
              key={opt.key}
              onClick={() => {
                setCondition(opt.key);
                setSingleValue("");
                setMultiValues([]);
                setStartDate(null);
                setEndDate(null);
              }}
              className={clsx(
                "flex items-start gap-3 p-2 rounded-md hover:bg-gray-50 cursor-pointer",
                condition === opt.key && "bg-white border border-purple-200"
              )}
            >
              <Radio
                value={opt.key}
                className="mt-1 text-gray-300"
                color="purple"
              />

              <div className="flex-1">
                <div className="text-subhead font-medium text-gray-600">
                  {opt.label}
                </div>
                {opt.hasValue && condition === opt.key && (
                  <div
                    className="mt-2 -ml-[calc(1rem+0.75rem)]"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                    }}
                  >
                    {isDateCondition(opt.key) ? (
                      <DateRangePicker
                        viewMonth={viewMonth}
                        onChangeViewMonth={setViewMonth}
                        value={{ start: startDate, end: endDate }}
                        onChange={({ start, end }) => {
                          if (opt.key === "is-between") {
                            if (
                              start &&
                              end &&
                              start.getTime() > end.getTime()
                            ) {
                              setStartDate(end);
                              setEndDate(start);
                            } else {
                              setStartDate(start);
                              setEndDate(end);
                            }
                          } else {
                            setStartDate(start);
                            setEndDate(null);
                          }
                        }}
                        mode={opt.key === "is-between" ? "range" : "single"}
                      />
                    ) : opt.multiSelect ? (
                      <MultiSelectCombobox
                        options={(
                          valueOptions?.[opt.key] ??
                          defaultValueOptions?.[opt.key] ??
                          []
                        ).map((item: any) =>
                          typeof item === "string"
                            ? { id: item, name: item }
                            : item
                        )}
                        selectedValues={multiValues}
                        onChange={setMultiValues}
                        placeholder={valuePlaceholder}
                        optionsTitle={optionsTitle}
                        className="w-full"
                      />
                    ) : (
                      <Combobox<string>
                        options={
                          (valueOptions?.[opt.key] ??
                            defaultValueOptions?.[opt.key] ??
                            []) as string[]
                        }
                        displayValue={(v) => v ?? ""}
                        placeholder={valuePlaceholder}
                        value={singleValue}
                        onChange={(v) => setSingleValue(v ?? "")}
                        onQueryChange={(v) => setSingleValue(v)}
                        className="w-full"
                        optionsTitle={optionsTitle}
                      >
                        {(val: string) => (
                          <ComboboxOption
                            key={val}
                            value={val}
                            className="truncate"
                          >
                            {val}
                          </ComboboxOption>
                        )}
                      </Combobox>
                    )}
                  </div>
                )}
              </div>
            </label>
          ))}
        </RadioGroup>
      </div>

      <div className="flex-shrink-0 bg-white border-t border-gray-200">
        <div className="flex items-center justify-end p-4 gap-2">
          <Button
            type="button"
            color="white"
            className="!border !border-gray-300"
            onClick={onCancel}
          >
            Cancel
          </Button>
          <Button type="button" color="purple" onClick={handleSave}>
            Save
          </Button>
        </div>
      </div>
    </div>
  );
}
