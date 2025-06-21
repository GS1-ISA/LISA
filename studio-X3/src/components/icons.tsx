
import type { SVGProps } from 'react';

export function AppLogo(props: SVGProps<SVGSVGElement>) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 100 40"
      width="100"
      height="40"
      aria-label="ISA Logo"
      {...props}
    >
      <rect width="100%" height="100%" fill="transparent" />
      <text
        x="50%"
        y="50%"
        dominantBaseline="middle"
        textAnchor="middle"
        fontFamily="var(--font-geist-sans), Arial, sans-serif"
        fontSize="28"
        fontWeight="bold"
        fill="hsl(var(--sidebar-foreground))"
      >
        ISA
      </text>
    </svg>
  );
}

// You can add more custom icons here if needed
