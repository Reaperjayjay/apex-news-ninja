import { cn } from "@/lib/utils";
import { motion, type Transition } from "framer-motion";
import { ReactNode } from "react";

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  style?: React.CSSProperties;
}

export const GlassCard = ({ children, className, hover = true, style }: GlassCardProps) => {
  const Component = hover ? motion.div : 'div';
  const hoverProps = hover ? {
    whileHover: { y: -4 },
    transition: { duration: 0.2 } as Transition
  } : {};

  return (
    <Component
      className={cn("glass rounded-2xl p-6 transition-all", className)}
      style={{
        boxShadow: '0 4px 20px rgba(0, 212, 255, 0.08)',
        ...style
      }}
      {...hoverProps}
    >
      {children}
    </Component>
  );
};
