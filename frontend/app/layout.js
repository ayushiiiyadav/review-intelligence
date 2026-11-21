import { Anton, Bricolage_Grotesque, Courier_Prime } from "next/font/google";
import "./globals.css";

const headline = Anton({ subsets: ["latin"], weight: "400", variable: "--font-headline" });
const display = Bricolage_Grotesque({ subsets: ["latin"], variable: "--font-display" });
const receipt = Courier_Prime({ subsets: ["latin"], weight: ["400", "700"], variable: "--font-receipt" });

export const metadata = {
  title: "Review Intelligence",
  description: "Compare two apps using NLP analysis of public user reviews",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${headline.variable} ${display.variable} ${receipt.variable}`}>
      <body>{children}</body>
    </html>
  );
}