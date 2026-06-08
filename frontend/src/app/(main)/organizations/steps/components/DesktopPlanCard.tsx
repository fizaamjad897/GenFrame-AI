"use client";

import { Button } from "@/components/ui/button";
import { LucideIcon } from "lucide-react";

interface PlanCardProps {
  id: string;
  name: string;
  price: number;
  description: string;
  icon: LucideIcon;
  iconColor?: string;
  iconBg?: string;
  isSelected: boolean;
  onSelect: (id: string) => void;
}

export function PlanCard({
  id,
  name,
  price,
  description,
  icon: Icon,
  iconColor = "text-purple-200",
  iconBg = "bg-purple-50",
  isSelected,
  onSelect,
}: PlanCardProps) {
  return (
    <div
      onClick={() => onSelect(id)}
      className="cursor-pointer transition-all duration-200"
    >
      <div className="p-3 lg:p-4 text-center">
        {/* Icon with outer and inner circle backgrounds */}
        <div className="w-12 h-12 lg:w-14 lg:h-14 rounded-full bg-purple-25 flex items-center justify-center mx-auto mb-3 lg:mb-4">
          <div className="w-9 h-9 lg:w-10 lg:h-10 rounded-full bg-primary-100 flex items-center justify-center">
            <Icon className={`w-5 h-5 lg:w-6 lg:h-6 ${iconColor}`} />
          </div>
        </div>

        {/* Plan Name */}
        <h3 className="text-base lg:text-lg font-semibold text-purple-400 mb-1">
          {name}
        </h3>

        {/* Price */}
        <div className="mb-2">
          <span className="text-2xl lg:text-3xl font-bold text-gray-900">
            ${price}
          </span>
          <span className="text-sm lg:text-base text-gray-600">/mth</span>
        </div>

        {/* Description */}
        <p className="text-xs lg:text-subhead font-regular text-gray-500 mb-3 lg:mb-4 min-h-[2.5rem] lg:min-h-[3rem] flex items-center justify-center">
          {description}
        </p>

        {/* Get Started Button */}
        {isSelected ? (
          <Button
            type="button"
            outline
            className="text-sm w-full border-gray-200 text-gray-700 bg-white hover:bg-gray-50"
          >
            Current Plan
          </Button>
        ) : (
          <Button
            type="button"
            color="purple"
            className="text-sm w-full"
          >
            Choose this plan
          </Button>
        )}
      </div>
    </div>
  );
}
