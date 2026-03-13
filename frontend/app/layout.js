import { Fraunces, Instrument_Sans } from "next/font/google";

import "./globals.css";

const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-display",
});

const instrumentSans = Instrument_Sans({
  subsets: ["latin"],
  variable: "--font-body",
});

export const metadata = {
  title: "GreenTrace",
  description:
    "Trace how company sustainability claims compare with NGO, news, and outside-source reporting.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={`${fraunces.variable} ${instrumentSans.variable}`}>
        {children}
      </body>
    </html>
  );
}
