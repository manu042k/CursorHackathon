import type { ButtonHTMLAttributes } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type Props = ButtonHTMLAttributes<HTMLButtonElement>;

export function ButtonPrimary({ children, className = "", ...props }: Props) {
  return (
    <Button className={cn(className)} {...props}>
      {children}
    </Button>
  );
}
