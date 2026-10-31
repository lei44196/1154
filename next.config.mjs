/** @type {import('next').NextConfig} */
const nextConfig = {
  // 服务器约 2 GB 内存，限制构建并行度，减少内存峰值。
  experimental: { cpus: 1 },
};

export default nextConfig;
