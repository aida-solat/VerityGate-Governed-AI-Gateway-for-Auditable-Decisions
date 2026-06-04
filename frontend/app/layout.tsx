import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "@/components/ui/use-toast";

export const metadata: Metadata = {
  title: "VerityGate — Governed AI Gateway",
  description: "Route models. Verify evidence. Govern decisions.",
  authors: [{ name: "Deciwa", url: "https://github.com/deciwa" }],
  creator: "Deciwa",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="text-slate-200 antialiased">
        <Toaster>{children}</Toaster>
      </body>
    </html>
  );
}
