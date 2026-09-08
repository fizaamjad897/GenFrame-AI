"use client";

import React from "react";
import { X } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { Button } from "./button";
import { Input } from "./input";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  isLoading?: boolean;
  title?: string | React.ReactNode;
  children: React.ReactNode;
  footer?: React.ReactNode;
  size?: "sm" | "md" | "lg" | "xl" | "custom";
  showBackdrop?: boolean;
  backdropOpacity?: number;
  divider?: boolean;
}

export function Modal({
  isOpen,
  onClose,
  title,
  isLoading,
  children,
  footer,
  size = "md",
  showBackdrop = true,
  backdropOpacity = 0.3,
  divider = true,
}: ModalProps) {
  const sizeClasses = {
    sm: "max-w-md",
    md: "max-w-lg",
    lg: "max-w-2xl",
    xl: "max-w-4xl",
    custom: "max-w-[605px]"
  };

  return (
    <AnimatePresence>
      {isOpen && (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {showBackdrop && (
        <motion.div
          className="absolute inset-0 bg-black"
          initial={{ opacity: 0 }}
          animate={{ opacity: backdropOpacity }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.15 }}
          onClick={onClose}
        />
      )}

      {/* Modal */}
      <motion.div
        initial={{ opacity: 0, y: 8, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 8, scale: 0.98 }}
        transition={{ duration: 0.18, ease: [0.16, 1, 0.3, 1] }}
        className={`relative bg-white rounded-lg border border-dashed border-gray-200 w-full mx-4 ${sizeClasses[size]}`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 pt-6 pb-5">
          <h2 className="text-[24px] font-semibold text-gray-900">{title}</h2>
          <button
            onClick={onClose}
            disabled={isLoading}
            className="p-2 bg-purple-25 rounded-md transition-colors"
          >
            <X className="w-6 h-6 text-gray-900" />
          </button>
        </div>

        {/* Divider */}
        {divider &&
          <div className="h-px bg-gray-200" />
        }

        {/* Body */}
        <div className="p-6">{children}</div>

        {/* Footer */}
        {footer && (
          <>
            <div className="h-px bg-gray-200" />
            <div className="p-6">{footer}</div>
          </>
        )}
      </motion.div>
    </div>
      )}
    </AnimatePresence>
  );
}

export function ModalInput({
  label,
  ...inputProps
}: {
  label: string;
} & React.ComponentProps<typeof Input>) {
  return (
    <div>
      <label className="block text-subhead font-medium text-gray-700 mb-2">
        {label}
      </label>
      <Input {...inputProps} />
    </div>
  );
}

export function ModalActions({
  onCancel,
  onSubmit,
  submitLabel = "Create",
  cancelLabel = "Cancel",
  isLoading = false,
  isSubmitDisabled = false,
}: {
  onCancel: () => void;
  onSubmit: () => void;
  submitLabel?: string;
  cancelLabel?: string;
  isLoading?: boolean;
  isSubmitDisabled?: boolean;
}) {
  return (
    <div className="flex justify-end gap-3">
      <Button
        color="white"
        className="!border !border-gray-300"
        onClick={onCancel}
        disabled={isLoading}
      >
        {cancelLabel}
      </Button>
      <Button
        color="purple"
        onClick={onSubmit}
        disabled={isLoading || isSubmitDisabled}
      >
        {submitLabel}
      </Button>
    </div>
  );
}
