# 零到全栈 · Next.js 前端与 FastAPI 后端

项目已迁移到 Next.js 15，使用文件夹路由、页面预渲染和静态导出，通过 Nginx 发布。自定义文案、原有布局、动画和输入计数均保留。

后端位于 `backend/`，实现主页数据、真实拼音与情感分析、自动文档与 SQLite 存档。模块 6.6 已加入 Cookie 会话和前端历史弹窗：每个浏览器只查看自己的记录，重启后数据仍在。安装、运行和验证方法见 [backend/README.md](backend/README.md)。

## 本地开发

```bash
npm install
npm run dev
```

打开 `http://localhost:3000`。主页路径是 `/`，文字实验室是 `/text-lab`。

## 项目结构

- `app/layout.jsx`：全站 HTML 外壳和 CSS 入口。
- `app/page.jsx`：主页路由。
- `app/text-lab/page.jsx`：文字实验室路由。
- `components/`：导航、页面、卡片和动画组件。
- `data/site.js`：集中管理网站文案，改这里即可修改标题等内容。
- `css/`：沿用前面课程的样式。
- `next.config.mjs`：`output: "export"` 启用静态导出；构建并行度为 1，适应现有约 2 GB 内存的服务器。

Next 的文件夹路由接替了旧的 `App.jsx` 和 `useRoute.js`，导航使用 Next 的 `Link`。
交互组件标记 `"use client"`；页面内容仍会在构建时预渲染成 HTML。

## 构建

```bash
npm run build
```

生成的 `out/` 包含 `index.html`、`text-lab.html`、`404.html` 和 `_next/` 资源，可直接交给 Nginx。
`node_modules/`、`.next/`、`out/` 和旧的 `dist/` 均不提交到 Git。

当前采用 4.6 的静态导出方案，生产环境由 Nginx 服务 `out/`，无需运行 `npm run start`。该命令用于未开启静态导出的 Next 服务模式。
如果 Windows 环境的 Next 遥测配置写入报跨盘错误，可以先设置 `$env:NEXT_TELEMETRY_DISABLED = '1'` 再构建。

## 发布流程

本地 `git add`、`git commit`、`git push` 后，服务器执行：

```bash
cd /root/1154
node -v
git pull --ff-only
npm install
npm run build
```

服务器使用 nvm 管理 Node.js 24。新 shell 若找不到 Node，可执行 `. "$HOME/.nvm/nvm.sh"`。

Nginx 配置核心内容：

```nginx
root /root/1154/out;
index index.html;

location / {
    try_files $uri $uri.html $uri/ =404;
}
```

`/text-lab` 会找到真实的 `out/text-lab.html`，不需要回退到首页。不存在的页面返回 404。
修改配置后执行 `nginx -t` 和 `systemctl reload nginx`。

文字实验室已通过模块 5.5 的请求与状态更新显示后端结果。模块 6.2 的真实分析仅替换后端实现，接口约定不变。
