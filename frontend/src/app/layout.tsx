import type { ReactNode } from "react";
import { Space_Grotesk, Inter, IBM_Plex_Mono } from "next/font/google";
import { AppNav } from "@/components/AppNav";
import "./globals.css";
import "./shell.css";
import "./paper.css";

const display = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-display-face",
  weight: ["400", "500"],
});

const body = Inter({
  subsets: ["latin"],
  variable: "--font-body-face",
});

const mono = IBM_Plex_Mono({
  subsets: ["latin"],
  variable: "--font-mono-face",
  weight: ["400"],
});

export const metadata = {
  title: "Counterfactual Replay",
  description: "Twin-run market simulation",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className={`${body.className} ${body.variable} ${display.variable} ${mono.variable} antialiased`}>
        <AppNav />
        {children}
      </body>
    </html>
  );
}
