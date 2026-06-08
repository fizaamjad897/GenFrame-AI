"use client";

import { Fragment } from "react";
import { Dialog, Transition } from "@headlessui/react";
import clsx from "clsx";

interface SlideRightPanelProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  className?: string;
  width?: string; // e.g. w-[420px]
}

export function SlideRightPanel({
  isOpen,
  onClose,
  children,
  className,
  width = "w-[420px]",
}: SlideRightPanelProps) {
  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-40" onClose={onClose}>
        {/* Mobile backdrop only */}
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-200"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-150"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/30 lg:hidden" />
        </Transition.Child>

        <div className="fixed inset-0 lg:left-[272px] lg:top-2 lg:right-2 lg:bottom-2 overflow-hidden pointer-events-auto">
          <div className="absolute inset-0 flex justify-end pointer-events-auto">
            <Transition.Child
              as={Fragment}
              enter="transform transition ease-out duration-300"
              enterFrom="translate-x-full"
              enterTo="translate-x-0"
              leave="transform transition ease-in duration-200"
              leaveFrom="translate-x-0"
              leaveTo="translate-x-full"
            >
              <Dialog.Panel
                className={clsx(
                  "h-full bg-white shadow-md rounded-l-lg",
                  "overflow-auto lg:overflow-hidden",
                  width,
                  className
                )}
              >
                {children}
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}

export default SlideRightPanel;
