/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  // This is a placeholder. Further configuration will be added based on audit findings.
  // For now, we'll keep it minimal.
  // Warning: This allows production builds to successfully complete even if
  // your project has ESLint errors. This is temporary for initial setup.
  ignoreBuildErrors: true,
  eslint: {
    ignoreDuringBuilds: true, // Use this for ESLint errors during build
  },
};

module.exports = nextConfig;