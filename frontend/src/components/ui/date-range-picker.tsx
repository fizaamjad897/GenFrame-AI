"use client";

import React, { useMemo } from "react";
import clsx from "clsx";
import { ChevronLeft, ChevronRight } from "lucide-react";

function startOfMonth(date: Date) {
  return new Date(date.getFullYear(), date.getMonth(), 1);
}

function addMonths(date: Date, n: number) {
  return new Date(date.getFullYear(), date.getMonth() + n, 1);
}

function formatShortMonthYear(date: Date) {
  return date.toLocaleString(undefined, { month: "long", year: "numeric" });
}

function formatShortDate(date?: Date) {
  if (!date) return "";
  return date.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function normalize(d: Date) {
  return new Date(d.getFullYear(), d.getMonth(), d.getDate());
}

export type DateRange = { start: Date | null; end: Date | null };

interface Props {
  viewMonth: Date;
  onChangeViewMonth: (d: Date) => void;
  value: DateRange;
  onChange: (v: DateRange) => void;
  mode?: "range" | "single";
}

export default function DateRangePicker({
  viewMonth,
  onChangeViewMonth,
  value,
  onChange,
  mode = "range",
}: Props) {
  const [hoveredButton, setHoveredButton] = React.useState<
    "prev" | "next" | null
  >(null);

  const weeks = useMemo(() => {
    const first = startOfMonth(viewMonth);
    const days: Date[] = [];
    const startWeekDay = (first.getDay() + 6) % 7;
    const start = new Date(first);
    start.setDate(first.getDate() - startWeekDay);

    for (let i = 0; i < 42; i++) {
      const d = new Date(start);
      d.setDate(start.getDate() + i);
      days.push(d);
    }

    const rows: Date[][] = [];
    for (let i = 0; i < days.length; i += 7) rows.push(days.slice(i, i + 7));
    return rows;
  }, [viewMonth]);

  const handleDayClick = (d: Date, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    const day = normalize(d);
    if (mode === "single") {
      onChange({ start: day, end: null });
      return;
    }

    const { start, end } = value;
    if (!start || (start && end)) {
      onChange({ start: day, end: null });
    } else if (start && !end) {
      const s = normalize(start);
      if (day.getTime() >= s.getTime()) onChange({ start: s, end: day });
      else onChange({ start: day, end: s });
    }
  };

  const handlePrevMonth = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    onChangeViewMonth(addMonths(viewMonth, -1));
  };

  const handleNextMonth = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    onChangeViewMonth(addMonths(viewMonth, 1));
  };

  const inRange = (d: Date) => {
    const n = normalize(d);
    if (!value.start) return false;
    if (!value.end) return n.getTime() === normalize(value.start).getTime();
    return (
      n.getTime() >= normalize(value.start).getTime() &&
      n.getTime() <= normalize(value.end).getTime()
    );
  };

  return (
    <div
      className="bg-white rounded-lg p-2 w-full box-border"
      onClick={(e) => {
        e.preventDefault();
        e.stopPropagation();
      }}
      onMouseDown={(e) => {
        e.preventDefault();
        e.stopPropagation();
      }}
    >
      {/* Month navigation */}
      <div className="flex items-center justify-between mb-4 pointer-events-auto">
        <button
          type="button"
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            handlePrevMonth(e);
          }}
          onMouseEnter={() => setHoveredButton("prev")}
          onMouseLeave={() => setHoveredButton(null)}
          className={clsx(
            "rounded flex-shrink-0 p-2 pointer-events-auto transition-colors ml-4",
            hoveredButton === "prev" ? "bg-gray-100" : "bg-transparent"
          )}
        >
          <ChevronLeft className="h-5 w-5 text-gray-500" />
        </button>

        <div className="text-sm font-medium text-gray-700 flex-1 text-center min-w-0 truncate px-2">
          {formatShortMonthYear(viewMonth)}
        </div>

        <button
          type="button"
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            handleNextMonth(e);
          }}
          onMouseEnter={() => setHoveredButton("next")}
          onMouseLeave={() => setHoveredButton(null)}
          className={clsx(
            "rounded flex-shrink-0 p-2 pointer-events-auto transition-colors mr-4",
            hoveredButton === "next" ? "bg-gray-100" : "bg-transparent"
          )}
        >
          <ChevronRight className="h-5 w-5 text-gray-500" />
        </button>
      </div>

      {/* Date inputs */}
      <div className="flex items-center justify-center gap-3 mb-3 min-w-0">
        <input
          type="text"
          readOnly
          value={formatShortDate(value.start ?? undefined)}
          placeholder="Start"
          className="flex-1 min-w-0 w-0 max-w-36 rounded-lg border border-gray-300 px-3 py-1.5 text-sm bg-white text-gray-900 truncate shadow-sm"
        />
        {mode === "range" && (
          <>
            <div className="flex items-center justify-center flex-shrink-0">
              <div
                className="w-1.5 h-px bg-gray-500 rounded"
                aria-hidden="true"
              />
            </div>
            <input
              type="text"
              readOnly
              value={formatShortDate(value.end ?? undefined)}
              placeholder="End"
              className="flex-1 min-w-0 w-0 max-w-36 rounded-lg border border-gray-300 px-3 py-1.5 text-sm bg-white text-gray-900 truncate shadow-sm"
            />
          </>
        )}
      </div>

      {/* Weekday headers */}
      <div className="grid grid-cols-7 gap-0 mb-1">
        {["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"].map((day) => (
          <div
            key={day}
            className="h-5 flex items-center justify-center text-xs font-medium text-gray-700"
          >
            {day}
          </div>
        ))}
      </div>

      {/* Calendar grid */}
      <div className="grid grid-cols-7 gap-x-0 gap-y-1 pointer-events-auto">
        {weeks.map((week, i) => (
          <React.Fragment key={i}>
            {week.map((day, dayIndex) => {
              const isCurrentMonth = day.getMonth() === viewMonth.getMonth();
              const selected = inRange(day);
              const isStart =
                value.start &&
                normalize(day).getTime() === normalize(value.start).getTime();
              const isEnd =
                value.end &&
                normalize(day).getTime() === normalize(value.end).getTime();

              const isFirstOfWeek = dayIndex === 0;
              const isLastOfWeek = dayIndex === 6;

              const roundLeft = isStart || (selected && isFirstOfWeek);
              const roundRight = isEnd || (selected && isLastOfWeek);

              return (
                <div
                  key={day.toISOString()}
                  className="h-10 flex items-center justify-center pointer-events-none relative z-0"
                >
                  {value.start &&
                    value.end &&
                    selected &&
                    !(isStart && isEnd) && (
                      <div
                        className={clsx(
                          "absolute top-0 h-10 bg-[#F9F5FF] z-[-1]",
                          isStart ? "right-0 w-1/2" : isEnd ? "left-0 w-1/2" : "inset-0"
                        )}
                      />
                    )}
                  <button
                    type="button"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      handleDayClick(day, e);
                    }}
                    className={clsx(
                      "h-10 w-10 flex items-center justify-center text-sm rounded-full transition-colors cursor-pointer pointer-events-auto",
                      !isCurrentMonth && "text-gray-400",
                      isCurrentMonth &&
                        !selected &&
                        "text-gray-900 hover:bg-gray-100",
                      selected && !isStart && !isEnd && "text-[#6941C6]",
                      (isStart || isEnd) &&
                        "bg-[#7F56D9] text-white font-medium"
                    )}
                  >
                    {day.getDate()}
                  </button>
                </div>
              );
            })}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}
