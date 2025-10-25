import { Head, Html, Main, NextScript } from "next/document";

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        {/* Title should be defined at page level, not in _document */}
        {/* Using Georgia serif font as fallback - no external font loading needed */}
      </Head>
      <body style={{ margin: 0, padding: 0, overflow: "hidden" }}>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
