"use client";

import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cn } from "@/lib/utils";

type Variant = "primary" | "ghost" | "approve" | "reject" | "outline";
type Size = "sm" | "md" | "icon";

const variants: Record<Variant, string> = {
  primary: "bg-accent text-white hover:opacity-90",
  ghost: "bg-transparent text-slate-300 hover:bg-white/10",
  outline: "border border-white/10 bg-panel2 text-slate-200 hover:bg-white/10",
  approve: "bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30",
  reject: "bg-rose-500/20 text-rose-300 hover:bg-rose-500/30",
};

const sizes: Record<Size, string> = {
  sm: "h-7 px-3 text-xs",
  md: "h-10 px-4 text-sm",
  icon: "h-9 w-9",
};

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center gap-2 rounded-lg font-medium outline-none transition-colors focus-visible:ring-2 focus-visible:ring-accent disabled:opacity-50 disabled:pointer-events-none",
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button };
