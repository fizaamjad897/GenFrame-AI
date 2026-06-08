"use client";

import React, { useState } from "react";
import { LayoutGroup, motion } from "motion/react";
import { ArrowLeft } from "lucide-react";
import clsx from "clsx";
import FilterSearch from "./FilterSearch";
import FilterList from "./FilterList";
import editorsRegistry from "./editors";
import { SidebarHeader, SidebarBody, SidebarDivider } from "../sidebar";
import { X } from "lucide-react";

export interface FilterItem {
  id: string;
  title: string;
  icon?: React.ReactNode;
  expanded?: boolean;
  subtitle?: string;
}

interface AddFilterPanelProps {
  items?: FilterItem[];
  className?: string;
  onClose?: () => void;
  onAddFilter?: (payload: {
    id: string;
    condition: string;
    value?: string;
  }) => void;
  editors?: Record<string, React.ComponentType<any>>;
}

export default function AddFilterPanel({
  items = [],
  className,
  onClose,
  onAddFilter,
  editors,
}: AddFilterPanelProps) {
  const [query, setQuery] = useState("");
  const [activeId, setActiveId] = useState<string | null>(null);

  const filtered = items.filter((i) =>
    i.title.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div
      className={clsx(
        "w-full h-full bg-white rounded-l-lg shadow-sm flex flex-col",
        className
      )}
    >
      <SidebarHeader className="bg-gray-50 px-4 sticky top-0 z-10">
        <div className="flex items-center justify-between min-h-[44px]">
          <div className="flex items-center gap-2">
            {activeId ? (
              <button
                type="button"
                onClick={() => setActiveId(null)}
                className="p-2 rounded-md text-gray-900 bg-purple-25 cursor-pointer"
                aria-label="Back"
              >
                <ArrowLeft className="h-5 w-5" />
              </button>
            ) : null}

            <h2 className="text-heading-h2 ml-1 font-bold text-gray-900">
              {activeId
                ? items.find((i) => i.id === activeId)?.title || ""
                : "Add Filter"}
            </h2>
            {activeId && items.find((i) => i.id === activeId)?.subtitle && (
              <div className="text-heading-h2 font-regular text-gray-900">
                {items.find((i) => i.id === activeId)?.subtitle}
              </div>
            )}
          </div>

          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="p-2 rounded-md text-gray-900 bg-purple-25 flex items-center justify-center cursor-pointer"
          >
            <X className="h-6 w-6 text-gray-900" />
          </button>
        </div>

        {!activeId && (
          <div className="mt-4 w-full  border border-gray-200 rounded-md shadow-sm">
            <FilterSearch
              value={query}
              onChange={setQuery}
              placeholder="Search here"
            />
          </div>
        )}
      </SidebarHeader>

      <SidebarBody className="!p-0">
        <div className="flex-1 overflow-hidden min-h-0 relative">
          <div
            className="absolute inset-0 overflow-hidden"
            style={{ WebkitOverflowScrolling: "touch" } as React.CSSProperties}
          >
            <LayoutGroup>
              <motion.div
                key={activeId ? "editor" : "list"}
                initial={{ opacity: 0, x: 40 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -40 }}
                transition={{ duration: 0.18 }}
                className="h-full"
              >
                {!activeId ? (
                  <div className="h-full overflow-y-auto scrollbar-subtle">
                    <FilterList
                      items={filtered}
                      onOpenEditor={(id) => setActiveId(id)}
                    />
                  </div>
                ) : (
                  <div className="h-full flex flex-col overflow-hidden">
                    {activeId &&
                      (() => {
                        const map = editors || editorsRegistry;
                        const Editor = map ? map[activeId] : null;
                        if (!Editor) return null;
                        return (
                          <Editor
                            onCancel={() => setActiveId(null)}
                            onSave={(payload: any) => {
                              onAddFilter &&
                                onAddFilter({
                                  id: activeId,
                                  condition: payload.condition,
                                  value: payload.value,
                                });
                              setActiveId(null);
                            }}
                          />
                        );
                      })()}
                  </div>
                )}
              </motion.div>
            </LayoutGroup>
          </div>
        </div>
      </SidebarBody>
    </div>
  );
}
