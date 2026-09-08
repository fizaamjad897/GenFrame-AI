"use client";

/**
 * Shared Terminal Ledger motion primitives — the same entrance/hover language
 * used on the marketing site (frontend/src/app/page.tsx), extracted so every
 * app page picks up consistent, purposeful motion instead of one-off tweens.
 */
import React from "react";
import { motion, AnimatePresence } from "motion/react";
import { usePathname } from "next/navigation";
import { ease } from "@/app/theme/terminal";

/** Scroll-triggered fade + rise. Use for content below the first viewport. */
export function FadeIn({
  children,
  delay = 0,
  style,
  className,
}: {
  children: React.ReactNode;
  delay?: number;
  style?: React.CSSProperties;
  className?: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{ duration: 0.4, delay, ease }}
      style={style}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/** Guaranteed mount animation — use for above-the-fold / immediately-visible content. */
export function PopIn({
  children,
  delay = 0,
  style,
  className,
}: {
  children: React.ReactNode;
  delay?: number;
  style?: React.CSSProperties;
  className?: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay, ease }}
      style={style}
      className={className}
    >
      {children}
    </motion.div>
  );
}

/** Staggers its children's mount-in, one PopIn beat apart — for card grids/lists. */
export function StaggerGroup({
  children,
  step = 0.06,
  style,
  className,
}: {
  children: React.ReactNode[];
  step?: number;
  style?: React.CSSProperties;
  className?: string;
}) {
  return (
    <div style={style} className={className}>
      {React.Children.map(children, (child, i) => (
        <PopIn delay={i * step}>{child}</PopIn>
      ))}
    </div>
  );
}

/** Flat hover/press affordance for clickable cards — lift + border brighten, no shadow. */
export const hoverCard = {
  whileHover: { y: -2 },
  whileTap: { y: 0, scale: 0.995 },
  transition: { duration: 0.15, ease },
};

/** Wraps route content so navigating between app pages cross-fades instead of jump-cutting. */
export function PageTransition({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={pathname}
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -6 }}
        transition={{ duration: 0.22, ease }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}
