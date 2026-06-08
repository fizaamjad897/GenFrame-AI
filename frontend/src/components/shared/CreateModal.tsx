import React, { useState } from "react";
import { Modal, ModalInput, ModalActions } from "@/components/ui/modal";

interface CreateModalProps {
  open: boolean;
  currName?: string;
  onCancel: () => void;
  onSubmit: (name: string) => void;
}
const CreateModal: React.FC<CreateModalProps> = ({
  open,
  currName,
  onCancel,
  onSubmit,
}) => {
  const [value, setValue] = useState<string>(currName || "");

  return (
    <div>
      <Modal
        isOpen={open}
        onClose={onCancel}
        title="Create Compositon"
        footer={
          <ModalActions
            onCancel={onCancel}
            onSubmit={() => {
              if (!value.trim()) return;
              onSubmit(value.trim());
              //   setValue("");
              onCancel();
            }}
            submitLabel="Create"
          />
        }
      >
        <ModalInput
          label="Composition Name"
          // id="folder-name"
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Enter Composition name"
        />
      </Modal>
    </div>
  );
};

export default CreateModal;
