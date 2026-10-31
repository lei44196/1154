# 零到全栈 · 模块 4.5

本项目由 4.4 的 Vite + React 迁移到 Next.js 15，保留自定义文案、卡片布局、动画和输入计数。

## 本地运行

```bash
npm install
npm run dev
```

打开 `http://localhost:3000`，文字实验室路径为 `/text-lab`。

## 项目结构

- `app/layout.jsx`：全站 HTML 外壳和 CSS 入口。
- `app/page.jsx`：主页路由。
- `app/text-lab/page.jsx`：文字实验室路由。
- `components/`：导航、页面、卡片和动画组件。
- `data/site.js`：集中管理网站文案。
- `css/`：沿用前面课程的样式。

Next.js 的文件夹路由接替旧的 `App.jsx` 和 `useRoute.js`，导航使用 Next 的 `Link`。
交互组件标记 `"use client"`，纯展示组件保持默认服务端组件。
构建并行度限制为 1，以适应现有约 2 GB 内存的服务器。

## 4.5 构建

```bash
npm run build
npm run start
```

`.next/server/app/` 中能看到预渲染的 HTML，但 `.next/` 不是可直接交给 Nginx 的静态网站根目录。
下一节 4.6 会启用静态导出，生成 `out/` 后通过 Nginx 发布。
