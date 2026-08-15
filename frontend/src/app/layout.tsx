import type { ReactNode } from "react";
import { Space_Grotesk, Inter, IBM_Plex_Mono } from "next/font/google";
import { AnnouncementBar } from "@/components/AnnouncementBar";
import { AppNav } from "@/components/AppNav";
import "./globals.css";
import "./shell.css";

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
  description: "Controlled experiment — not a forecast",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className={`${display.variable} ${body.variable} ${mono.variable}`}>
        <AnnouncementBar />
        <AppNav />
        {children}
      </body>
    </html>
  );
}
