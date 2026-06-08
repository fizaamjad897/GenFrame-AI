"use client";

import clsx from "clsx";
import { useState, useRef, useEffect } from "react";
import { ChevronDown, X } from "lucide-react";
import { Checkbox } from "./checkbox";

export function MultiSelectCombobox<T extends { id: string; name: string }>({
  options,
  selectedValues = [],
  onChange,
  filter,
  optionsTitle,
  className,
  placeholder,
  autoFocus,
  disabled,
  "aria-label": ariaLabel,
}: {
  options: T[];
  selectedValues?: T[];
  onChange: (values: T[]) => void;
  filter?: (value: T, query: string) => boolean;
  optionsTitle?: string;
  className?: string;
  placeholder?: string;
  autoFocus?: boolean;
  disabled?: boolean;
  "aria-label"?: string;
}) {
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const filteredOptions =
    query === ""
      ? options
      : options.filter((option) =>
          filter
            ? filter(option, query)
            : option.name?.toLowerCase().includes(query.toLowerCase())
        );

  const handleSelect = (option: T) => {
    const isSelected = selectedValues.some((v) => v.id === option.id);
    if (isSelected) {
      onChange(selectedValues.filter((v) => v.id !== option.id));
    } else {
      onChange([...selectedValues, option]);
    }
  };

  const handleRemove = (option: T) => {
    onChange(selectedValues.filter((v) => v.id !== option.id));
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={clsx(
          "relative w-full cursor-default rounded-md bg-white max-h-60 py-1.5 pl-3 pr-10 text-left text-gray-900 shadow-sm border border-gray-300 focus:outline-none sm:text-sm hover:ring-gray-400 transition-colors h-input",
          disabled && "opacity-50 cursor-not-allowed bg-gray-50",
          className
        )}
      >
        <div className="flex flex-wrap gap-1 items-center min-h-[24px]">
          {selectedValues.length > 0 ? (
            selectedValues.map((value) => (
              <span
                key={value.id}
                className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-800"
              >
                {value.name}
                <span
                  role="button"
                  tabIndex={0}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRemove(value);
                  }}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      handleRemove(value);
                    }
                  }}
                  className="text-gray-400 hover:text-gray-400 cursor-pointer"
                >
                  <X className="h-3 w-3" />
                </span>
              </span>
            ))
          ) : (
            <span className="block truncate text-gray-500">
              {placeholder || "Select options"}
            </span>
          )}
        </div>

        <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
          <ChevronDown
            className={clsx(
              "h-4 w-4 text-gray-900 transition-transform",
              isOpen && "rotate-180"
            )}
            aria-hidden="true"
          />
        </span>
      </button>

      {isOpen && (
        <div className="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-xl bg-gray-50 py-1.5 shadow-lg ring-1 ring-zinc-950/10 focus:outline-none sm:text-sm">
          {optionsTitle && (
            <div className="px-4 pt-3 pb-1">
              <div className="text-subhead text-gray-600">{optionsTitle}</div>
            </div>
          )}
          {filteredOptions.map((option) => {
            const isSelected = selectedValues.some((v) => v.id === option.id);
            return (
              <div
                key={option.id}
                className={clsx(
                  "relative cursor-pointer select-none py-2.5 pl-3.5 pr-2 hover:bg-gray-50",
                  "text-gray-900"
                )}
                onClick={(e) => {
                  e.stopPropagation();
                  handleSelect(option);
                }}
              >
                <div className="flex items-center gap-3">
                  <Checkbox
                    checked={isSelected}
                    onChange={() => {}}
                    className="pointer-events-none"
                    color="primary"
                  />
                  <span
                    className={clsx(
                      "block truncate",
                      isSelected ? "font-medium" : "font-normal"
                    )}
                  >
                    {option.name}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
