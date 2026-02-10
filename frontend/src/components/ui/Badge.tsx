import { cn } from "@/lib/utils";

type BadgeVariant =
  | "domain"
  | "pii"
  | "public"
  | "internal"
  | "external"
  | "neutral";

const variantStyles: Record<BadgeVariant, string> = {
  domain: "bg-domain text-domain-text",
  pii: "bg-pii text-pii-text",
  public: "bg-public text-public-text",
  internal: "bg-internal text-internal-text",
  external: "bg-external text-external-text",
  neutral: "bg-surface-sunken text-text-secondary",
};

interface BadgeProps {
  variant: BadgeVariant;
  children: React.ReactNode;
  className?: string;
  dot?: boolean;
}

export function Badge({ variant, children, className, dot }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-[11px] font-semibold tracking-wide uppercase",
        variantStyles[variant],
        className
      )}
    >
      {dot && (
        <span
          className={cn("inline-block h-1.5 w-1.5 rounded-full", {
            "bg-domain-text": variant === "domain",
            "bg-pii-text": variant === "pii",
            "bg-public-text": variant === "public",
            "bg-internal-text": variant === "internal",
            "bg-external-text": variant === "external",
            "bg-text-secondary": variant === "neutral",
          })}
        />
      )}
      {children}
    </span>
  );
}
