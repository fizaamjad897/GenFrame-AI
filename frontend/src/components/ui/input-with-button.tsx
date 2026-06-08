"use client";

import React, { useState } from "react";
import { clsx } from "clsx";
import { Button } from "./button";
import { Input, InputGroup } from "./input";
import { Plus, X } from "lucide-react";

interface Chip {
  id: string;
  label: string;
  icon?: React.ReactNode;
  onRemove?: () => void;
}

interface InputWithButtonProps {
  // Input props
  id?: string;
  placeholder?: string;
  value?: string | number;
  onChange?: (value: string) => void;
  type?: "search" | "text" | "email" | "password" | "number";

  // Input enable/disable
  enableInput?: boolean;

  // Action props
  enableAction?: boolean;
  onAction?: () => void;

  // Chips display (optional)
  chips?: Chip[];
  maxVisibleChips?: number;

  // Icons
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;

  // Right button (optional)
  rightButton?: {
    label?: string;
    icon?: React.ReactNode;
    onClick?: () => void;
    iconOnly?: boolean;
    color?:
      | "white"
      | "dark/zinc"
      | "light"
      | "dark/white"
      | "dark"
      | "zinc"
      | "indigo"
      | "cyan"
      | "red"
      | "orange"
      | "amber"
      | "yellow"
      | "lime"
      | "green"
      | "emerald"
      | "teal"
      | "sky"
      | "blue"
      | "violet"
      | "purple"
      | "fuchsia"
      | "pink"
      | "rose";
    size?: "xs" | "sm" | "lg" | "base";
    className?: string;
  };

  // Styling
  width?: string;
  height?: string;
  className?: string;
  inputClassName?: string;

  // Container
  containerClassName?: string;
}

export function InputWithButton({
  id,
  placeholder = "",
  value = "",
  onChange,
  type = "text",
  enableInput = true,
  enableAction = false,
  onAction,
  leftIcon,
  rightIcon,
  rightButton,
  chips,
  maxVisibleChips = 1,
  width = "w-full",
  height = "!h-[38px]",
  className,
  inputClassName,
  containerClassName,
}: InputWithButtonProps) {
  const [isInputFocused, setIsInputFocused] = useState(false);
  const [isButtonFocused, setIsButtonFocused] = useState(false);

  // If input is disabled but action is enabled, show only action button
  if (!enableInput && enableAction && onAction) {
    return (
      <Button
        color="white"
        onClick={onAction}
        className="inline-flex items-center gap-1.5 text-gray-600 hover:bg-gray-50"
      >
        <Plus className="w-4 h-4 text-purple-500" />
        Add Action
      </Button>
    );
  }

  // If input is disabled and no action, return null
  if (!enableInput) {
    return null;
  }

  const hasChips = chips && chips.length > 0;
  const visibleChips = chips?.slice(0, maxVisibleChips) || [];
  const hiddenChipsCount = chips
    ? Math.max(0, chips.length - maxVisibleChips)
    : 0;
  const shouldHidePlaceholder = hasChips && value === "";

  // Parse chip label to separate name from details
  const parseChipLabel = (label: string) => {
    const match = label.match(/^([^(]+)\s*(?:\((.+)\))?$/);
    if (match) {
      return {
        name: match[1].trim(),
        details: match[2] ? match[2] : "",
      };
    }
    return { name: label, details: "" };
  };

  return (
    <div
      className={clsx(
        "relative flex items-center rounded-lg border-[1px] shadow-[0px_1px_2px_0px_#0000000D] border-gray-200 gap-1 px-1",
        isInputFocused && "border-primary",
        width,
        height,
        className
      )}
    >
      {leftIcon && (
        <div className="flex items-center justify-start pl-2">{leftIcon}</div>
      )}

      <Input
        id={id}
        unstyled
        type={type}
        placeholder={shouldHidePlaceholder ? "" : placeholder}
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        onFocus={() => setIsInputFocused(true)}
        onBlur={() => setIsInputFocused(false)}
        className="flex-1 min-w-0 autofill:bg-transparent autofill:shadow-[inset_0_0_0px_1000px_white] [-webkit-autofill]:bg-transparent [-webkit-autofill]:shadow-[inset_0_0_0px_1000px_white]"
      />

      {hasChips && (
        <div className="flex items-center gap-1.5 ml-auto pr-1">
          {visibleChips.map((chip, index) => {
            const { name, details } = parseChipLabel(chip.label);
            const isLastChip = index === visibleChips.length - 1;
            const showBadge = isLastChip && hiddenChipsCount > 0;

            return (
              <div
                key={chip.id}
                className="inline-flex items-center gap-1 px-2 py-2 bg-gray-50 rounded-md text-xs whitespace-nowrap"
              >
                {chip.icon && (
                  <span className="flex-shrink-0 text-primary">
                    {chip.icon}
                  </span>
                )}
                <span className="font-bold text-gray-800">{name}</span>
                {details && <span className="text-gray-600">{details}</span>}
                {showBadge && (
                  <>
                    <span className="text-gray-600">and</span>
                    <div className="inline-flex items-center justify-center px-1.5 py-0.5 bg-purple-25 rounded-full">
                      <span
                        className="text-xs font-medium"
                        style={{ color: "#7F56D9" }}
                      >
                        +{hiddenChipsCount}
                      </span>
                    </div>
                  </>
                )}
                {chip.onRemove && (
                  <button
                    onClick={chip.onRemove}
                    className="ml-0.5 inline-flex items-center justify-center hover:bg-gray-50 rounded transition-colors cursor-pointer"
                  >
                    <X className="w-3 h-3 text-primary" />
                  </button>
                )}
              </div>
            );
          })}
        </div>
      )}

      {rightIcon && (
        <div className="flex items-center justify-center pr-1">{rightIcon}</div>
      )}

      {rightButton && (
        <div
          className={clsx(
            "relative rounded-[4px] transition-all",
            isButtonFocused && !rightButton.iconOnly && "ring ring-primary",
            // when icon-only, constrain wrapper size, prevent growth and center content
            rightButton.iconOnly &&
            "w-8 h-8 flex-shrink-0 flex items-center justify-center border border-dashed border-primary overflow-hidden box-border"
          )}
        >
          <Button
            color={rightButton.color || "white"}
            size={rightButton.size || "xs"}
            onClick={() => rightButton.onClick?.()}
            onFocus={() => setIsButtonFocused(true)}
            onBlur={() => setIsButtonFocused(false)}
            className={clsx(
              "!rounded-[4px] before:!rounded-[4px] after:!rounded-[4px] transition-colors cursor-pointer",
              isButtonFocused &&
              "!border-transparent !outline-none [&]:!border-0",
              rightButton.iconOnly &&
              "!box-border !m-0 !w-full !h-full !p-0 !shadow-none !border-0 data-hover:!border-transparent data-active:!border-transparent !text-purple-25",
              !rightButton.iconOnly && "!shadow-[0px_1px_2px_0px_#0000000D]",
              rightButton.className
            )}
          >
            {rightButton.icon}
            {!rightButton.iconOnly && rightButton.label}
          </Button>
        </div>
      )}
    </div>
  );
}

export default InputWithButton;
