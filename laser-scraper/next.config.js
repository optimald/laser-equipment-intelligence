/** @type {import('next').NextConfig} */
const nextConfig = {
  async redirects() {
    return [
      {
        source: '/(.*)',
        destination: '/laser-procurement-frontend/$1',
        permanent: false,
      },
    ]
  },
}

module.exports = nextConfig
