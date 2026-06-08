import clsx from "clsx";

export function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={clsx("animate-pulse rounded-md bg-gray-200", className)}
      {...props}
    />
  );
}

// 2. The Agency Bar Skeleton
export function AgencyBarSkeleton({ className }: { className?: string }) {
  return (
    <div
      className={clsx(
        "bg-purple-25/50 p-3 rounded-lg w-full overflow-hidden border border-purple-100/20",
        className,
      )}
    >
      <div className="flex flex-wrap items-center gap-3">
        {/* Avatar Section */}
        <div className="flex-shrink-0 w-full lg:w-auto ml-1 flex items-center gap-3">
          <Skeleton className="h-10 w-10 rounded-full" />
          <div className="space-y-1.5">
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-3 w-48" />
          </div>
        </div>

        {/* Metrics Section */}
        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 xl:ml-auto ml-1 mt-2 lg:mt-0">
          {/* Status */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <Skeleton className="h-4 w-12" />
            <Skeleton className="h-6 w-16 rounded-full" />
          </div>

          <div className="hidden sm:block h-6 w-px bg-gray-300/50 flex-shrink-0" />

          {/* Licence */}
          <div className="flex-shrink-0">
            <div className="flex items-center gap-2">
              <Skeleton className="h-4 w-14" />
              <Skeleton className="h-4 w-8" />
            </div>
            <div className="mt-1">
              <Skeleton className="h-2 w-[120px] rounded-full" />
            </div>
          </div>

          <div className="hidden sm:block h-6 w-px bg-gray-300/50 flex-shrink-0" />

          {/* Members */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <Skeleton className="h-4 w-12" />
            <Skeleton className="h-2.5 w-2.5 rounded-full" />
            <Skeleton className="h-4 w-8" />
            <Skeleton className="h-4 w-16 opacity-50" />
          </div>

          <div className="hidden sm:block h-6 w-px bg-gray-300/50 flex-shrink-0" />

          {/* Next Charge */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-24" />
            {/* <Skeleton className="h-8 w-8 rounded-full ml-2" /> */}
          </div>
        </div>
      </div>
    </div>
  );
}
