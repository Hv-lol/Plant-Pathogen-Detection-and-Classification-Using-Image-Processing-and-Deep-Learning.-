/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "standalone",
  images: {
    remotePatterns: [
      {
        protocol: "http",
        hostname: "localhost",
        port: "8000",
        pathname: "/api/v1/storage/**",
      },
      {
        protocol: "https",
        hostname: "**",
        pathname: "/api/v1/storage/**",
      },
    ],
  },
};

module.exports = nextConfig;
