"use client";

import React from "react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

interface AnimatedButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  className?: string;
  variant?: "primary" | "secondary" | "outline" | "destructive";
  size?: "default" | "lg" | "sm";
  fullWidth?: boolean;
}

export const AnimatedButton = ({
  children,
  className,
  variant = "primary",
  size = "default",
  fullWidth = false,
  ...props
}: AnimatedButtonProps) => {
  const variants = {
    primary: "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-500/25",
    secondary: "bg-zinc-800 text-white hover:bg-zinc-700 shadow-lg shadow-zinc-900/25",
    outline: "bg-transparent border-2 border-zinc-700 text-white hover:bg-zinc-900/30 shadow-lg shadow-zinc-900/10",
    destructive: "bg-gradient-to-r from-red-600 to-rose-600 text-white shadow-lg shadow-red-500/25"
  };

  const sizes = {
    default: "px-6 py-2.5 text-sm",
    lg: "px-8 py-3 text-base",
    sm: "px-4 py-2 text-xs"
  };

  return (
    <motion.button
      whileHover={{ scale: 1.02, translateY: -2 }}
      whileTap={{ scale: 0.98 }}
      className={cn(
        "relative rounded-full font-medium overflow-hidden group transition-all duration-200",
        variants[variant],
        sizes[size],
        fullWidth && "w-full",
        className
      )}
      {...props}
    >
      {variant === "primary" && (
        <span className="absolute inset-0 w-full h-full bg-gradient-to-br from-blue-500 to-purple-600 opacity-0 group-hover:opacity-50 transition-opacity duration-300 blur-xl"></span>
      )}
      {variant === "destructive" && (
        <span className="absolute inset-0 w-full h-full bg-gradient-to-br from-red-500 to-rose-600 opacity-0 group-hover:opacity-50 transition-opacity duration-300 blur-xl"></span>
      )}
      <span className="relative flex items-center justify-center gap-2">
        {children}
      </span>
    </motion.button>
  );
}; 