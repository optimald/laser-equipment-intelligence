/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['lasermatch.io', 'localhost'],
  },
  env: {
    API_BASE_URL: process.env.API_BASE_URL || 'http://localhost:8000',
  },
}

module.exports = nextConfig
