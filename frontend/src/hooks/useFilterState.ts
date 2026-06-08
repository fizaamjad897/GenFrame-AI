import { useState, useCallback } from "react";

export interface SelectedFilter {
  id: string;
  title: string;
  icon?: React.ReactNode;
  condition?: string;
  value?: any;
}

export interface FilterChip {
  id: string;
  label: string;
  icon?: React.ReactNode;
  onRemove?: () => void;
}

function formatValue(value: any): string {
  if (!value) return "";

  if (value instanceof Date) {
    return value.toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  }

  if (Array.isArray(value)) {
    return value
      .map((v) => (typeof v === "object" ? v.name || JSON.stringify(v) : v))
      .join(", ");
  }

  if (typeof value === "object") {
    if (value.start || value.end) {
      const start = value.start
        ? formatValue(new Date(value.start))
        : "Start";
      const end = value.end ? formatValue(new Date(value.end)) : "End";
      return `${start} - ${end}`;
    }
     // Handle generic objects with name property
    if (value.name) return value.name;

    return JSON.stringify(value);
  }

  return String(value);
}

const CONDITION_LABELS: Record<string, string> = {
  is: "is",
  "is-not": "is not",
  "start-with": "starts with",
  "not-start-with": "does not start with",
  "ends-with": "ends with",
  "not-ends-with": "does not end with",
  contains: "contains",
  "not-contains": "does not contain",
  empty: "is empty",
  "not-empty": "is not empty",
  "is-greater-than-or-equal": "is >=",
  "is-less-than": "is <",
  "is-less-than-or-equal": "is <=",
  "overlap-with": "overlaps with",
  "not-overlap-with": "does not overlap with",
  "items-start-with": "items start with",
  "not-items-start-with": "items do not start with",
  "items-ends-with": "items end with",
  "not-items-ends-with": "items do not end with",
  "is-between": "is between",
  "is-before": "is before",
  "is-after": "is after",
  on: "is on",
  "not-on": "is not on",
  Enabled: "is Enabled",
  Disabled: "is Disabled",
};

export function useFilterState() {
  const [selectedFilters, setSelectedFilters] = useState<SelectedFilter[]>([]);

  const addFilter = useCallback((filter: SelectedFilter) => {
    setSelectedFilters((prev) => [
      ...prev.filter((f) => f.id !== filter.id),
      filter,
    ]);
  }, []);

  const removeFilter = useCallback((filterId: string) => {
    setSelectedFilters((prev) => prev.filter((f) => f.id !== filterId));
  }, []);

  const removeAllFilters = useCallback(() => {
    setSelectedFilters([]);
  }, []);

  const getFilterChips = useCallback((): FilterChip[] => {
    return selectedFilters.map((filter) => {
      // Build label with condition and value if available
      let label = filter.title;
      const displayValue = formatValue(filter.value);

      if (filter.condition || displayValue) {
        // Map invalid/raw condition to readable label, fallback to original if not found
        const safeCondition = filter.condition ?? "";
        const readableCondition =
          CONDITION_LABELS[safeCondition] || safeCondition.replace(/-/g, " ");

        const parts = [readableCondition, displayValue].filter(Boolean);

        if (parts.length > 0) {
          label = `${filter.title} (${parts.join(" ")})`;
        }
      }

      return {
        id: filter.id,
        label,
        icon: filter.icon,
        onRemove: () => removeFilter(filter.id),
      };
    });
  }, [selectedFilters, removeFilter]);

  return {
    selectedFilters,
    addFilter,
    removeFilter,
    removeAllFilters,
    getFilterChips,
  };
}
