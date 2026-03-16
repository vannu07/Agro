/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    unoptimized: true,
    domains: ['localhost', 'krishi-mitr.vercel.app'],
  },
  rewrites: async () => {
    return {
      beforeFiles: [
        {
          source: '/api/:path*',
          destination: 'http://localhost:5000/api/:path*',
        },
        {
          source: '/crop-recommend',
          destination: 'http://localhost:5000/crop-recommend',
        },
        {
          source: '/disease-predict',
          destination: 'http://localhost:5000/disease-predict',
        },
        {
          source: '/fertilizer',
          destination: 'http://localhost:5000/fertilizer',
        },
        {
          source: '/yield',
          destination: 'http://localhost:5000/yield',
        },
        {
          source: '/sustainability',
          destination: 'http://localhost:5000/sustainability',
        },
        {
          source: '/irrigation',
          destination: 'http://localhost:5000/irrigation',
        },
        {
          source: '/market-trends',
          destination: 'http://localhost:5000/market-trends',
        },
      ],
    };
  },
  headers: async () => {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
