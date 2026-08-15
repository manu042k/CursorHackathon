import type { ButtonHTMLAttributes } from "react";

type Props = ButtonHTMLAttributes<HTMLButtonElement>;

export function ButtonPrimary({ children, className = "", ...props }: Props) {
  return (
    <button type="button" className={`button-primary ${className}`.trim()} {...props}>
      {children}
    </button>
  );
}
