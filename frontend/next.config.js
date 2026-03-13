/** @type {import("next").NextConfig} */
const nextConfig = {
  turbopack: {
    root: __dirname,
  },
  async rewrites() {
    return [
      {
        source: "/api/backend/:path*",
        destination: `${
          process.env.NEXT_PUBLIC_BACKEND_API_URL || "http://127.0.0.1:8000"
        }/:path*`, // Proxy to Backend
      },
    ];
  },
};

module.exports = nextConfig;
