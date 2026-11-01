# 零到全栈 · 文字实验室

输入中文，返回情感分数、倾向标签和带声调的拼音，并把分析结果保存在 SQLite 中。
每个浏览器通过 Cookie 会话查看自己的历史。主页文案也从后端接口获取。

模块 7.1 已完成全栈上线：前端由 Nginx 的 80 端口提供，后端在 8000 端口运行。
线上地址：<http://123.57.184.86/text-lab>。

## 技术栈与结构

- 前端：Next.js 15、React、animejs，静态导出到 `out/`。
- 后端：Python、FastAPI、Uvicorn；SnowNLP 分析情感，pypinyin 生成拼音。
- 存储：Python 标准库 sqlite3，数据库为 `backend/history.db`。
- 部署：Nginx 提供静态文件，`nohup` 让后端在 SSH 断开后继续运行。

`app/` 定义页面路由和全站外壳；`components/` 拼装页面、卡片和历史弹窗；
`css/` 管理样式；`data/site.js` 提供静态文案和主页请求失败时的后备内容。
`backend/main.py` 处理 API，`backend/storage.py` 负责存储。
接口、数据库演进和验证示例见 [后端说明](backend/README.md)。

## 配置说明

真实配置、依赖、构建产物、日志与数据库不提交到 Git。两份 `.env.example` 随源码提交。

| 位置 | 配置键 | 本地 | 当前服务器 |
| --- | --- | --- | --- |
| 前端 `.env.local` / `.env.production` | `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | `http://123.57.184.86:8000` |
| 后端 `backend/.env` | `ALLOWED_ORIGINS` | `http://localhost:3000` | `http://123.57.184.86` |

`ALLOWED_ORIGINS` 是允许发请求的前端来源，多个值使用英文逗号分隔。
线上 HTTP 的默认 80 端口不用写，也不要写成开发时的 3000。
`NEXT_PUBLIC_` 配置会进入浏览器，不能填密码或密钥。

后端通过 python-dotenv 读取同目录 `.env`，进程环境变量优先；修改后需重启后端。
前端公开配置在构建时写入 JS：开发时改完重启 `npm run dev`，线上改完重新构建。
Next.js 构建时 `.env.local` 优先于 `.env.production`，所以服务器没有本地开发用的 `.env.local`。

## Windows 本地开发

需要 Node.js 18.18+ 和 Python 3.10+；本项目当前本地环境使用 Python 3.13。
在项目根目录首次准备后端：

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
```

已有配置时保留原文件，不重复复制。然后启动后端：

```powershell
cd backend
$env:PYTHONUTF8 = '1'
.\.venv\Scripts\fastapi.exe dev main.py
```

另开一个终端，在项目根目录首次准备并启动前端：

```powershell
npm ci
Copy-Item .env.example .env.local
npm run dev
```

浏览器打开 <http://localhost:3000> 或 <http://localhost:3000/text-lab>。
本地前后端统一使用 `localhost`，以便 Cookie 正常携带。
日常保存源码即可看开发效果，不用每次构建。

## 服务器部署（7.1）

以下命令已在 Ubuntu 24.04、Python 3.12、Node.js 24 环境走通。
云平台安全组已放行 80 和 8000 端口；项目位于 `/root/1154`。

先在本地提交并推送需要发布的源码，然后 SSH 登录服务器：

```bash
cd /root/1154
git pull --ff-only
. /root/.nvm/nvm.sh
node -v
python3 --version
command -v python3
```

首次部署前端时，复制样例并编辑 `.env.production`，使用上表的服务器地址：

```bash
cp .env.example .env.production
vim .env.production
chmod 600 .env.production
```

已有配置时保留原文件。安装依赖并构建：

```bash
npm ci --no-audit --no-fund
NEXT_TELEMETRY_DISABLED=1 npm run build
```

`out/` 包含 `index.html`、`text-lab.html`、`404.html` 和 `_next/`。
重新构建会更新该目录的产物，Nginx 直接提供新文件，无需运行 `npm run start`。
每次发布前可将现有 `out/` 复制到项目外备份，便于回退。

首次部署后端时创建独立虚拟环境。Ubuntu 若缺 venv，先安装组件：

```bash
sudo apt-get install -y python3-venv
cd /root/1154/backend
python3 -m venv --prompt=zero-to-tech .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
cp .env.example .env
vim .env
chmod 600 .env
```

按上表写入线上 `ALLOWED_ORIGINS`。已有环境和配置时无需重新创建或覆盖。
确认 8000 上没有旧后端占用后，启动后台服务：

```bash
cd /root/1154/backend
nohup .venv/bin/fastapi run main.py --host 0.0.0.0 --port 8000 > backend.log 2>&1 < /dev/null &
echo $! > backend.pid
```

`history.db` 会自动初始化。线上数据库独立于本地数据库，拉取代码不会同步或清空数据。
`nohup` 保证 SSH 断开后继续运行；服务器重启或进程崩溃后仍需手动启动。
systemd 和同源反向代理留到 7.2。

Nginx 当前核心配置：

```nginx
root /root/1154/out;
index index.html;

location / {
    try_files $uri $uri.html $uri/ =404;
}
```

仅修改 Nginx 配置时需要 `nginx -t && systemctl reload nginx`。

## 检查与后续更新

```bash
curl -fsS http://localhost:8000/api/profile
ss -lntp 'sport = :8000'
tail -n 50 /root/1154/backend/backend.log
```

访问线上文字实验室做一次分析，打开历史记录；换浏览器或无痕窗口，历史应互相隔离。
关闭 SSH 窗口后再访问，后端应仍能响应。

后续前端更新：拉取代码、`npm ci`、`npm run build`。
后端更新后还需要安装变化的 Python 依赖并重启；先检查 PID 对应的确实是本项目：

```bash
cd /root/1154/backend
ps -p "$(cat backend.pid)" -o pid,args
```

确认是本项目的 FastAPI 进程后，停止该 PID，再执行上面的 `nohup` 命令并更新 `backend.pid`。
更新时保留 `history.db` 和 `.env`。

2026-11-01 已验证：线上生产构建、前端路由与 JS/CSS、公开 API、CORS 预检、
两组独立 Cookie 的分析及历史隔离、SQLite 完整性、SSH 断开后服务可达。
两条验证记录只属于验证时的会话。浏览器自动点击验证因工具连接故障未执行。
