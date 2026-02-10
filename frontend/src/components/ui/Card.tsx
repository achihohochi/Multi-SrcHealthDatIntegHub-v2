import { cn } from "@/lib/utils";

interface CardProps {
  children: React.ReactNode;
  className?: string;
  interactive?: boolean;
  padding?: "sm" | "md" | "lg";
}

const paddingMap = {
  sm: "p-3",
  md: "p-4 sm:p-5",
  lg: "p-5 sm:p-6",
};

export function Card({
  children,
  className,
  interactive = false,
  padding = "md",
}: CardProps) {
  return (
    <div
      className={cn(
        "card-base",
        paddingMap[padding],
        interactive && "card-interactive cursor-pointer",
        className
      )}
    >
      {children}
    </div>
  );
}
