"use client";

import { Button } from "@/components/ui/button";
import {
  LucideIcon,
  ChevronDown,
  ChevronUp,
  Check,
  Minus,
  HelpCircle,
} from "lucide-react";
import { useState } from "react";

interface Feature {
  name: string;
  hasInfo?: boolean;
  included: boolean;
}

interface MobilePlanCardProps {
  id: string;
  name: string;
  price: number;
  description: string;
  icon: LucideIcon;
  iconColor?: string;
  iconBg?: string;
  isSelected: boolean;
  onSelect: (id: string) => void;
  features: Feature[];
  genPlans?: boolean;
  genButton?: string;
  creditCount?: string
}

export function MobilePlanCard({
  id,
  name,
  price,
  description,
  icon: Icon,
  iconColor = "text-purple-200",
  iconBg = "bg-purple-50",
  isSelected,
  onSelect,
  features,
  genPlans,
  genButton,
  creditCount,
}: MobilePlanCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div
      className={`rounded-2xl border-2 transition-all duration-200 ${isSelected
        ? "border-purple-200 bg-purple-25/30"
        : "border-gray-200 bg-white"
        }`}
    >
      {/* Card Header */}
      <div className="p-6 flex flex-col justify-center items-center">
        {/* Icon */}
        <div className="w-12 h-12 rounded-full bg-purple-25 flex items-center justify-center mb-4">
          <div className="w-9 h-9 rounded-full bg-primary-100 flex items-center justify-center">
            <Icon className={`w-5 h-5 ${iconColor}`} />
          </div>
        </div>

        {/* Plan Name */}
        <h3 className="text-xl font-semibold text-purple-400 mb-2">{name}</h3>

        {/* Price */}
        <div className="mb-3">
          <span className="text-3xl font-bold text-gray-900">${price}</span>
          <span className="text-gray-500 text-lg">/mth</span>
        </div>

        {/* Description */}
        <p className="text-sm text-gray-600 mb-4">{description}</p>

        {/* Get Started Button */}
        {genPlans ? <>
          {isSelected ?
            <Button
              type="button"
              outline
              className="w-full mb-3" >
              {genButton}
            </Button>
            :
            <Button
              type="button"
              color="purple"
              className="w-full mb-3" >
              {genButton}
            </Button>}
          <Button
            type="button"
            outline
            className="w-full mb-3"
          >
            {creditCount}
          </Button>
        </> :
          <>
            <Button
              type="button"
              color="purple"
              className="w-full mb-3"
              onClick={() => onSelect(id)}
            >
              {isSelected ? "Selected" : "Get Started"}
            </Button>

            {/* View Features Toggle */}
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="w-full flex items-center justify-center gap-2 text-purple-600 text-sm font-medium py-2"
            >
              {isExpanded ? (
                <>
                  Hide features
                  <ChevronUp className="w-4 h-4" />
                </>
              ) : (
                <>
                  View all features
                  <ChevronDown className="w-4 h-4" />
                </>
              )}
            </button>
          </>
        }
      </div>

      {/* Expandable Features List */}
      {isExpanded && (
        <div className="border-t border-gray-200">
          <div className="p-6 pt-4">
            <h4 className="text-sm font-semibold text-gray-900 mb-3">
              Features included:
            </h4>
            <div className="space-y-3">
              {features.map((feature, idx) => (
                <div key={idx} className="flex items-start gap-3">
                  <div className="flex-shrink-0 mt-0.5">
                    {feature.included ? (
                      <div className="w-5 h-5 rounded-full bg-green-100 flex items-center justify-center">
                        <Check className="w-3.5 h-3.5 text-green-600" />
                      </div>
                    ) : (
                      <div className="w-5 h-5 flex items-center justify-center">
                        <Minus className="w-4 h-4 text-gray-400" />
                      </div>
                    )}
                  </div>
                  <div className="flex-1">
                    <span
                      className={`text-sm ${feature.included ? "text-gray-900" : "text-gray-400"
                        }`}
                    >
                      {feature.name}
                    </span>
                    {feature.hasInfo && (
                      <HelpCircle className="w-4 h-4 text-gray-400 inline-block ml-2" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
