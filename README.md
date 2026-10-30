# 零到全栈 · 4.1 模块化成果

依据 [zero-to-tech-4-1](https://github.com/joylibo/zero-to-tech-demos/tree/main/zero-to-tech-4-1) 的页面与样式，已完成原 README 中的五步 ES 模块化改造。

## 本地运行

在本目录打开终端：

```powershell
python -m http.server 8000 --bind 127.0.0.1
```

浏览器访问 http://127.0.0.1:8000/，按 Ctrl+C 停止服务。ES 模块需要 HTTP 服务，请勿直接双击 HTML。anime.js 从 jsDelivr CDN 加载，需要联网。

## 文件结构

- `index.html`：个人主页。
- `text-lab.html`：文字实验室。
- `css/`：参考项目的八个样式文件。
- `js/main.js`：统一入口，初始化导航、卡片动画和分数动画。
- `js/nav.js`：导出 `initNav`，高亮当前页面导航。
- `js/cards.js`：导出 `initCardsAnim`，使用 anime.js 的 `animate` 和 `stagger`。
- `js/score.js`：导出 `initScoreAnim`，点击按钮播放 `scrambleText` 数字动画。

两个页面均只加载 `<script type="module" src="js/main.js"></script>`。anime.js 通过 ES 模块导入，不再依赖全局 `anime` 或传统脚本的加载顺序。

文字实验室沿用课程示例的固定文本、拼音和情感分数；按钮演示分数动画，尚未接入真实文本分析服务。
