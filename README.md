# 零到全栈 · 模块 4.4

React 双页面项目，按模块 4.4「升级我们的项目」及「把它发布到公网」完成改造。

## 本地开发

```bash
npm install
npm run dev
```

访问终端显示的本地地址。个人主页路径为 `/`，文字实验室为 `/text-lab`。

## 本章功能

- `src/data/site.js` 集中管理主页和文字实验室的文案。
- 输入框使用 React state，实时显示「已输入 N 字」。
- `src/router/useRoute.js` 同步地址栏、页面导航和浏览器前进后退。
- 结果卡暂时显示固定内容；真实分析将在后端接口章节接入。

`src/main.jsx` 是统一入口，`App.jsx` 选择页面，页面组合 `src/components/` 中的组件；样式由入口导入 `src/css/`。
旧的根目录 `css/`、`js/`、`text-lab.html` 和 `src/result.jsx` 保留为前面课程的参考，新版使用 `/` 和 `/text-lab`。

## 提交与部署

只提交源码和锁文件，`node_modules/`、`dist/` 已加入 `.gitignore`。
本地提交并 push 后，在服务器执行：

```bash
cd /root/1154
git pull --ff-only
npm install
npm run build
```

服务器使用 Node.js 24，通过 nvm 安装；新 shell 中可执行 `. "$HOME/.nvm/nvm.sh"` 加载 nvm。

Nginx 的 `root` 指向 `/root/1154/dist`，并在 `location /` 中设置：

```nginx
try_files $uri $uri/ /index.html;
```

这样直接访问或刷新 `/text-lab` 也会交给 React 路由。修改 Nginx 配置后执行 `nginx -t` 和 `systemctl reload nginx`。
