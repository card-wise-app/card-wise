import "./globals.css";
import type { Metadata } from "next";
import { WalletProvider } from "@/components/store";

export const metadata: Metadata = {
  title: "CardWise — Your cards. Your money. Your smartest move.",
  description: "Find out which of your credit cards gives you the maximum cashback and rewards on every purchase. No full card number, CVV or OTP ever required.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <WalletProvider>{children}</WalletProvider>
      </body>
    </html>
  );
}
