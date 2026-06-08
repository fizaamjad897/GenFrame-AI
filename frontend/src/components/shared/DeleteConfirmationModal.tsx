// DeleteConfirmationModal.tsx
"use client";

import React from "react";
import { Modal, ModalActions } from "@/components/ui/modal"; // adjust import path

interface DeleteConfirmationModalProps {
  type?: "unpublish" | "delete";
  isOpen: boolean;
  onClose: () => void;
  onSubmit: () => void;
  isLoading?: boolean;
  itemType?: string;
  itemName?: string;
  submitLabel?: string;
}

const DeleteConfirmationModal: React.FC<DeleteConfirmationModalProps> = ({
  isOpen,
  type = "delete",
  onClose,
  onSubmit,
  isLoading = false,
  itemType = "content",
  itemName,
  submitLabel,
}) => {
  const isUnpublish = type === "unpublish";

  // Default submit label if not provided
  const defaultSubmitLabel = isUnpublish ? "Unpublish" : "Delete";

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      isLoading={isLoading}
      title={isUnpublish ? `Unpublish ${itemType}` : `Delete ${itemType}`}
      footer={
        <ModalActions
          onCancel={onClose}
          onSubmit={onSubmit}
          isLoading={isLoading}
          submitLabel={
            isLoading
              ? `${defaultSubmitLabel}ing...`
              : submitLabel ?? defaultSubmitLabel
          }
          isSubmitDisabled={isLoading}
        />
      }
    >
      <div className="flex flex-col items-center text-center space-y-4 py-4">
        <div
          className={`flex items-center justify-center w-12 h-12 rounded-full ${
            isUnpublish ? "bg-yellow-100" : "bg-red-100"
          }`}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className={`h-6 w-6 ${
              isUnpublish ? "text-yellow-600" : "text-red-600"
            }`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v4m0 4h.01M21 12A9 9 0 113 12a9 9 0 0118 0z"
            />
          </svg>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            {isUnpublish
              ? `Are you sure you want to unpublish this ${itemType}?`
              : `Are you sure you want to delete this ${itemType}?`}
          </h3>
          <p className="text-sm text-gray-500 mt-1">
            {isUnpublish
              ? "Unpublishing will remove the content from the player, but it won't be deleted permanently."
              : "This action cannot be undone."}
            {itemName && (
              <>
                <br />
                <span className="font-medium text-gray-800">{itemName}</span>
              </>
            )}
          </p>
        </div>
      </div>
    </Modal>
  );
};

export default DeleteConfirmationModal;
