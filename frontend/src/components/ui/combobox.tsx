"use client";

import * as Headless from "@headlessui/react";
import clsx from "clsx";
import React, { useState } from "react";
import { ChevronDown } from "lucide-react";

export function Combobox<T>({
  options,
  displayValue,
  filter,
  anchor = "bottom",
  optionsTitle,
  className,
  placeholder,
  autoFocus,
  "aria-label": ariaLabel,
  children,
  onQueryChange,
  ...props
}: {
  options: T[];
  displayValue: (value: T | null) => string | undefined;
  filter?: (value: T, query: string) => boolean;
  optionsTitle?: string;
  className?: string;
  placeholder?: string;
  autoFocus?: boolean;
  "aria-label"?: string;
  children: (value: NonNullable<T>) => React.ReactElement;
} & Omit<Headless.ComboboxProps<T, false>, "as" | "multiple" | "children"> & {
    anchor?: "top" | "bottom";
    onQueryChange?: (q: string) => void;
  }) {
  const [query, setQuery] = useState("");

  const filteredOptions =
    query === ""
      ? options
      : options.filter((option) =>
          filter
            ? filter(option, query)
            : displayValue(option)?.toLowerCase().includes(query.toLowerCase())
        );

  return (
    <Headless.Combobox {...props} multiple={false} onClose={() => setQuery("")}>
      <span
        data-slot="control"
        className={clsx([
          className,
          // Basic layout
          "relative block w-full",
          // Background color + shadow on the element itself (avoid layering pseudo which caused inner line at 1px ring)
          "rounded-lg bg-white shadow-sm dark:bg-white/5 dark:shadow-none",
          // Focus ring
          "after:pointer-events-none after:absolute after:inset-0 after:rounded-lg after:ring-transparent after:ring-inset sm:focus-within:after:ring sm:focus-within:after:ring-[var(--color-gray-300)]",
          // Selected / active state: apply ring on element
          "data-[selected=true]:ring-[var(--color-primary)] data-[selected=true]:ring-1",
          // Disabled state
          "has-data-disabled:opacity-50 has-data-disabled:bg-zinc-950/5 has-data-disabled:shadow-none",
          // Invalid state
          "has-data-invalid:before:shadow-red-500/10",
        ])}
      >
        <Headless.ComboboxInput
          autoFocus={autoFocus}
          data-slot="control"
          aria-label={ariaLabel}
          displayValue={(option: T) => displayValue(option) ?? ""}
          onChange={(event) => {
            const v = event.target.value;
            setQuery(v);
            onQueryChange && onQueryChange(v);
          }}
          placeholder={placeholder}
          className={clsx([
            className,
            // Basic layout
            "relative block w-full appearance-none rounded-lg py-[calc(--spacing(2.5)-1px)] sm:py-[calc(--spacing(1.5)-1px)]",
            // Horizontal padding
            "pl-[calc(--spacing(3.5)-1px)] sm:pl-[calc(--spacing(3)-1px)]",
            options.length > 0
              ? "pr-[calc(--spacing(10)-1px)] sm:pr-[calc(--spacing(9)-1px)]"
              : "pr-[calc(--spacing(3.5)-1px)] sm:pr-[calc(--spacing(3)-1px)]",
            // Typography
            "text-base/6 text-gray-900 placeholder:text-gray-500 sm:text-sm/6",
            // Border
            "border border-gray-200 hover:border-gray-300",
            // Background color
            "bg-white",
            // Hide default focus styles
            "focus:outline-hidden",
            // Invalid state
            "data-invalid:border-red-500 data-invalid:data-hover:border-red-500 dark:data-invalid:border-red-500 dark:data-invalid:data-hover:border-red-500",
            // Disabled state
            "data-disabled:border-zinc-950/20 dark:data-disabled:border-white/15 dark:data-disabled:bg-white/2.5 dark:data-hover:data-disabled:border-white/15",
            // System icons
            "dark:scheme-dark",
          ])}
        />
        {options.length > 0 && (
          <Headless.ComboboxButton className="group absolute inset-y-0 right-0 flex items-center px-2">
            <ChevronDown
              className="size-5 stroke-zinc-500 group-data-disabled:stroke-zinc-600 group-data-hover:stroke-zinc-700 sm:size-4 dark:stroke-zinc-400 dark:group-data-hover:stroke-zinc-300 forced-colors:stroke-[CanvasText]"
              aria-hidden
              strokeWidth={1.5}
            />
          </Headless.ComboboxButton>
        )}
      </span>
      <Headless.ComboboxOptions
        transition
        anchor={anchor}
        className={clsx(
          // Anchor positioning
          "[--anchor-gap:--spacing(2)] [--anchor-padding:--spacing(4)] sm:data-[anchor~=start]:[--anchor-offset:-4px]",
          // Base styles,
          "isolate min-w-[calc(var(--input-width)+8px)] scroll-py-1 rounded-xl p-1 select-none empty:invisible",
          // Invisible border that is only visible in `forced-colors` mode for accessibility purposes
          "outline outline-transparent focus:outline-hidden",
          // Handle scrolling when menu won't fit in viewport
          "overflow-y-scroll overscroll-contain",
          // Popover background
          "bg-white shadow-xl ring-1 ring-black/5",
          // Transitions
          "transition-opacity duration-100 ease-in data-closed:data-leave:opacity-0 data-transition:pointer-events-none"
        )}
      >
        {optionsTitle && filteredOptions.length > 0 && (
          <div className="px-4 pt-3 pb-1">
            <div className="text-subhead text-gray-600">{optionsTitle}</div>
          </div>
        )}
        {filteredOptions.map((option, index) =>
          children(option as NonNullable<T>)
        )}
      </Headless.ComboboxOptions>
    </Headless.Combobox>
  );
}

export function ComboboxOption<T>({
  children,
  className,
  ...props
}: { className?: string; children?: React.ReactNode } & Omit<
  Headless.ComboboxOptionProps<"div", T>,
  "as" | "className"
>) {
  let sharedClasses = clsx(
    // Base
    "flex min-w-0 items-center",
    // Icons
    "*:data-[slot=icon]:size-5 *:data-[slot=icon]:shrink-0 sm:*:data-[slot=icon]:size-4",
    "*:data-[slot=icon]:text-zinc-500 group-data-focus/option:*:data-[slot=icon]:text-zinc-700",
    "forced-colors:*:data-[slot=icon]:text-[CanvasText] forced-colors:group-data-focus/option:*:data-[slot=icon]:text-[Canvas]",
    // Avatars
    "*:data-[slot=avatar]:-mx-0.5 *:data-[slot=avatar]:size-6 sm:*:data-[slot=avatar]:size-5"
  );

  return (
    <Headless.ComboboxOption {...props} as={"div"}>
      {({ active, selected }) => (
        <div
          className={clsx(
            // Basic layout
            "group/option grid w-full cursor-default grid-cols-[1fr_--spacing(5)] items-baseline gap-x-2 rounded-lg py-2.5 pr-2 pl-3.5 sm:grid-cols-[1fr_--spacing(4)] sm:py-1.5 sm:pr-2 sm:pl-3",
            // Typography
            "text-subhead text-gray-900",
            // Hover/focus
            active && "bg-gray-50",
            // Selected
            selected && "bg-purple-25 text-zinc-900",
            // Forced colors mode
            "forced-color-adjust-none forced-colors:data-focus:bg-[Highlight] forced-colors:data-focus:text-[HighlightText]",
            // Disabled
            "data-disabled:opacity-50"
          )}
        >
          <span className={clsx(className, sharedClasses)}>{children}</span>

          {selected && (
            <svg
              className="relative col-start-2 size-5 self-center stroke-current sm:size-4"
              viewBox="0 0 16 16"
              fill="none"
              aria-hidden="true"
            >
              <path
                d="M4 8.5l3 3L12 4"
                strokeWidth={1.5}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          )}
        </div>
      )}
    </Headless.ComboboxOption>
  );
}

export function ComboboxLabel({
  className,
  ...props
}: React.ComponentPropsWithoutRef<"span">) {
  return (
    <span
      {...props}
      className={clsx(
        className,
        "ml-2.5 truncate first:ml-0 sm:ml-2 sm:first:ml-0"
      )}
    />
  );
}

export function ComboboxDescription({
  className,
  children,
  ...props
}: React.ComponentPropsWithoutRef<"span">) {
  return (
    <span
      {...props}
      className={clsx(
        className,
        "flex flex-1 overflow-hidden text-zinc-500 group-data-focus/option:text-white before:w-2 before:min-w-0 before:shrink dark:text-zinc-400"
      )}
    >
      <span className="flex-1 truncate">{children}</span>
    </span>
  );
}
