import * as Headless from "@headlessui/react";
import clsx from "clsx";
import React, { forwardRef, useLayoutEffect, useRef, useState } from "react";
import { ChevronDown, Check } from "lucide-react";

interface SelectOption {
  value: string;
  label: string;
  icon?: React.ReactNode;
}

interface CustomSelectProps {
  value: string;
  selectMenuPosition?: "top-full" | "bottom-full";
  onChange: (value: string) => void;
  onOpenChange?: (isOpen: boolean) => void;
  options?: SelectOption[];
  placeholder?: string;
  className?: string;
  menuClassName?: string;
  disabled?: boolean;
  children?: React.ReactNode;
  maxHeight?: number;
}

export const Select = forwardRef<HTMLDivElement, CustomSelectProps>(
  function Select(
    {
      value,
      onChange,
      onOpenChange,
      options = [],
      placeholder = "Select option",
      className,
      menuClassName,
      disabled,
      children,
      selectMenuPosition,
      maxHeight: maxHeightLimit = 200,
    },
    ref
  ) {
    const selectedOption = options.find((option) => option.value === value);
    const [isOpen, setIsOpen] = useState(false);
    const [menuPosition, setMenuPosition] = useState<"top-full" | "bottom-full">("top-full");
    const [maxHeight, setMaxHeight] = useState<number>(maxHeightLimit);
    const menuRef = useRef<HTMLDivElement>(null);
    const buttonRef = useRef<HTMLButtonElement>(null);
    const positionCheckRef = useRef(false);

    // Notify parent when open state changes
    useLayoutEffect(() => {
      onOpenChange?.(isOpen);
    }, [isOpen, onOpenChange]);

    return (
      <div className={clsx("relative", className)} ref={ref}>
        <Headless.Menu as="div" className="relative">
          {({ open: headlessOpen }) => {
            // Calculate position when menu opens/closes - defer state updates to avoid render-time updates
            if (headlessOpen && buttonRef.current) {
              const buttonRect = buttonRef.current.getBoundingClientRect();
              if (buttonRect) {
                const viewportHeight = window.innerHeight;
                const spaceBelow = viewportHeight - buttonRect.bottom - 10;
                const spaceAbove = buttonRect.top - 10;
                const estimatedMenuHeight = Math.min(options.length * 40 + 16, maxHeightLimit);

                Promise.resolve().then(() => {
                  // If selectMenuPosition is explicitly set, use it
                  if (selectMenuPosition) {
                    setMenuPosition(selectMenuPosition);
                    setMaxHeight(
                      Math.min(
                        selectMenuPosition === "bottom-full" ? spaceAbove : spaceBelow,
                        maxHeightLimit
                      )
                    );
                  } else if (spaceBelow < estimatedMenuHeight && spaceAbove > spaceBelow) {
                    // Not enough space below and more space above - position above
                    setMenuPosition("bottom-full");
                    setMaxHeight(Math.min(spaceAbove, maxHeightLimit));
                  } else {
                    // Default: position below
                    setMenuPosition("top-full");
                    setMaxHeight(Math.min(spaceBelow, maxHeightLimit));
                  }
                });
              }
            }

            // Defer state update to avoid render-time updates
            if (headlessOpen !== isOpen) {
              Promise.resolve().then(() => {
                setIsOpen(headlessOpen);
                onOpenChange?.(headlessOpen);
              });
            }

            return (
              <>
                <span
                  data-slot="control"
                  className={clsx([
                    // Basic layout
                    "group relative block w-full",
                    // Background color + shadow applied to inset pseudo element, so shadow blends with border in light mode
                    "before:absolute before:inset-px before:rounded-[calc(var(--radius-lg)-1px)] before:bg-white before:shadow-sm",
                    // Background color is moved to control and shadow is removed in dark mode so hide `before` pseudo
                    "dark:before:hidden",
                    // Focus ring
                    "after:pointer-events-none after:absolute after:inset-0 after:rounded-lg after:ring-transparent after:ring-inset has-data-focus:after:ring-2 has-data-focus:after:ring-blue-500",
                    // Disabled state
                    "has-data-disabled:opacity-50 has-data-disabled:before:bg-zinc-950/5 has-data-disabled:before:shadow-none",
                  ])}
                >
                  <Headless.Menu.Button
                    ref={buttonRef}
                    disabled={disabled}
                    className={clsx([
                      // Basic layout
                      "relative block w-full appearance-none rounded-lg py-[calc(--spacing(2.5)-1px)] pr-[calc(--spacing(10)-1px)] sm:py-[calc(--spacing(1.5)-1px)] sm:pr-[calc(--spacing(9)-1px)]",
                      selectedOption?.icon
                        ? "pl-[calc(--spacing(9)-1px)]"
                        : "pl-[calc(--spacing(3.5)-1px)] sm:pl-[calc(--spacing(3)-1px)]",
                      "h-input",
                      // Typography
                      "text-left text-base/6 text-gray-600 sm:text-sm/6",
                      // Border
                      "border border-gray-300 focus:border-primary dark:border-gray-300 dark:focus:border-primary",
                      // Background color
                      "bg-background/75 backdrop-blur-xl dark:bg-background/75",
                      // Hide default focus styles
                      "focus:outline-hidden",
                      // Disabled state
                      "data-disabled:border-zinc-950/20 data-disabled:opacity-100 dark:data-disabled:border-white/15 dark:data-disabled:bg-white/2.5 dark:data-hover:data-disabled:border-white/15",
                    ])}
                  >
                    {selectedOption?.icon && (
                      <span className="absolute left-3 top-1/2 -translate-y-1/2 flex items-center text-gray-500">
                        {selectedOption.icon}
                      </span>
                    )}
                    <span
                      className={clsx(
                        "block truncate pr-4",
                        selectedOption ? "text-gray-600" : "text-gray-500"
                      )}
                    >
                      {selectedOption ? selectedOption.label : placeholder}
                    </span>
                  </Headless.Menu.Button>

                  <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
                    <ChevronDown className="w-4 h-4 stroke-gray-900 group-has-data-disabled:stroke-zinc-600" />
                  </span>
                </span>

                <Headless.Menu.Items
                  ref={menuRef}
                  style={{ maxHeight: `${maxHeight}px` }}
                  className={clsx(
                    // position the popover absolutely so it doesn't push other content
                    `absolute left-0 z-50 mt-2`,
                    // Dynamic positioning based on available space
                    menuPosition === "bottom-full" ? "bottom-full" : "top-full",
                    // Anchor positioning (kept as CSS vars, no behavior props)
                    "[--anchor-gap:--spacing(1)] [--anchor-padding:--spacing(1)]",
                    // Base styles
                    "isolate w-full min-w-[var(--button-width)] rounded-xl p-1",
                    // Invisible border that is only visible in `forced-colors` mode for accessibility purposes
                    "outline outline-transparent focus:outline-hidden",
                    // Handle scrolling when menu won't fit in viewport
                    "overflow-y-auto",
                    // Popover background
                    "bg-background dark:bg-background",
                    // Shadows
                    "shadow-lg ring-1 ring-gray-200/10 dark:ring-gray-200/10 dark:ring-inset",
                    // Transitions
                    "transition data-leave:duration-100 data-leave:ease-in data-closed:data-leave:opacity-0",
                    // Custom menu className
                    menuClassName
                  )}
                >
                  {children
                    ? children
                    : options.map((option) => (
                      <Headless.Menu.Item key={option.value}>
                        {({ active }) => (
                          <button
                            type="button"
                            onClick={() => onChange(option.value)}
                            className={clsx(
                              // Base styles
                              "group cursor-default rounded-lg px-3.5 py-2.5 focus:outline-hidden sm:px-3 sm:py-1.5 w-full",
                              // Text styles
                              "text-left text-sm font-normal text-gray-900",
                              "flex items-center gap-2",
                              // Active (focus) state
                              active && "bg-purple-25",
                              // Hover
                              "hover:bg-purple-25",
                              // Selected state
                              value === option.value &&
                              "bg-gray-50 font-semibold",
                              // Disabled state
                              "data-disabled:opacity-50"
                            )}
                          >
                            {option.icon && (
                              <span className="flex-shrink-0 text-gray-600">
                                {option.icon}
                              </span>
                            )}
                            <span className="flex-1">{option.label}</span>
                            {value === option.value && (
                              <Check className="w-4 h-4 text-primary flex-shrink-0" />
                            )}
                          </button>
                        )}
                      </Headless.Menu.Item>
                    ))}
                </Headless.Menu.Items>
              </>
            );
          }}
        </Headless.Menu>
      </div>
    );
  }
);
