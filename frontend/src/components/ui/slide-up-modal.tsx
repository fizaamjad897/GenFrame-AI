"use client";

import { Fragment } from "react";
import { Dialog, Transition } from "@headlessui/react";
import { X } from "lucide-react";
import clsx from "clsx";

interface SlideUpModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  className?: string;
  isUploadImage?: boolean
}

export function SlideUpModal({
  isOpen,
  onClose,
  children,
  className,
  isUploadImage = false
}: SlideUpModalProps) {
  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className={`fixed inset-0 ${isUploadImage ? "bg-transparent" : "bg-black/25"} `} />
        </Transition.Child>

        <div className="fixed inset-0 overflow-hidden">
          <div className="flex min-h-full items-end justify-center">
            <Transition.Child
              as={Fragment}
              enter="transform transition ease-out duration-300"
              enterFrom="translate-y-full"
              enterTo="translate-y-0"
              leave="transform transition ease-in duration-200"
              leaveFrom="translate-y-0"
              leaveTo="translate-y-full"
            >
              <Dialog.Panel
                // allow inner content to scroll horizontally when it overflows
                className={clsx(
                  "w-full transform bg-white transition-all relative",
                  "rounded-t-2xl border-t border-dashed border-gray-200",
                  "h-[calc(100vh-64px)]",
                  "overflow-auto",
                  "flex flex-col",
                  className
                )}
              >
                {/* Keep a flex container that can shrink; children may manage their own overflow */}
                <div className="flex-1 flex flex-col min-h-0">{children}</div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}
