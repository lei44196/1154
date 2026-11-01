# 零到全栈 · 文字实验室

输入中文，返回情感分数、倾向标签和带声调的拼音，并把分析结果保存在 SQLite 中。
每个浏览器通过 Cookie 会话查看自己的历史。主页文案也从后端接口获取。

模块 7.2 已完成同源部署：Nginx 在 80 端口提供静态前端，并把 `/api/` 转发给本机后端。
后端由 systemd 守护，只监听 `127.0.0.1:8000`，不直接对公网提供服务。
线上地址：<http://123.57.184.86/text-lab>。

## 技术栈与结构

- 前端：Next.js 15、React、animejs，静态导出到 `out/`。
- 后端：Python、FastAPI、Uvicorn；SnowNLP 分析情感，pypinyin 生成拼音。
- 存储：Python 标准库 sqlite3，数据库为 `backend/history.db`。
- 部署：Nginx 提供静态文件和反向代理，systemd 管理后端启动、自动恢复和日志。

`app/` 定义页面路由和全站外壳；`components/` 拼装页面、卡片和历史弹窗；
`css/` 管理样式；`data/site.js` 提供静态文案和主页请求失败时的后备内容。
`backend/main.py` 处理 API，`backend/storage.py` 负责存储。
`deploy/zero-backend.service` 是当前服务器的服务配置，`deploy/nginx-api.conf` 是代理配置片段。
接口、数据库演进和验证示例见 [后端说明](backend/README.md)。

## 配置说明

真实配置、依赖、构建产物、日志与数据库不提交到 Git。两份 `.env.example` 随源码提交。

| 位置 | 配置键 | 本地 | 当前服务器 |
| --- | --- | --- | --- |
| 前端 `.env.local` / `.env.production` | `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | 留空：`NEXT_PUBLIC_API_BASE_URL=` |
| 后端 `backend/.env` | `ALLOWED_ORIGINS` | `http://localhost:3000` | `http://123.57.184.86` |

`ALLOWED_ORIGINS` 是允许发请求的前端来源，多个值使用英文逗号分隔。
线上 HTTP 的默认 80 端口不用写，也不要写成开发时的 3000。
`NEXT_PUBLIC_` 配置会进入浏览器，不能填密码或密钥。
线上留空时，前端请求 `/api/profile`、`/api/analyze` 和 `/api/history`，自动使用当前页面的源。
以后更换域名或启用 HTTPS，也无需再为 API 修改地址。
保留 CORS 和 `credentials: "include"`，本地开发的 3000 → 8000 仍然是跨源请求。

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

## 服务器部署（7.2）

以下命令已在 Ubuntu 24.04、Python 3.12、Node.js 24 环境走通。
项目位于 `/root/1154`；安全组保留 SSH 和 HTTP 访问，8000 的公网放行规则已移除。

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
首次部署创建无登录权限的独立服务用户，并授予后端目录及 SQLite 所需权限：

```bash
id zero-backend >/dev/null 2>&1 || useradd --system --user-group --no-create-home --home-dir /nonexistent --shell /usr/sbin/nologin zero-backend
chown zero-backend:zero-backend /root/1154/backend
chgrp zero-backend /root/1154/backend/.env
chmod 640 /root/1154/backend/.env
if test -f /root/1154/backend/history.db; then
    chown zero-backend:zero-backend /root/1154/backend/history.db
    chmod 640 /root/1154/backend/history.db
fi
runuser -u zero-backend -- test -r /root/1154/backend/.env
```

当前服务器的 `/root` 允许目录穿越，已验证服务用户能访问项目；如果换服务器或目录，
先检查父目录权限并相应调整服务文件的绝对路径。只给后端目录和数据库写权限，源码和虚拟环境保持 root 所有。

安装并启动仓库内的 service 文件：

```bash
install -m 644 /root/1154/deploy/zero-backend.service /etc/systemd/system/zero-backend.service
systemd-analyze verify /etc/systemd/system/zero-backend.service
systemctl daemon-reload
systemctl enable --now zero-backend
systemctl --no-pager status zero-backend
```

首次从 7.1 迁移时，先核实并停止旧的 nohup 进程，避免争用 8000。
当前已完成迁移，旧 `backend.log` 和 PID 文件已归档到项目外的发布备份目录。

服务使用 `User=zero-backend`，工作目录为 `/root/1154/backend`，启动命令是：

```text
/root/1154/backend/.venv/bin/fastapi run main.py --host 127.0.0.1 --port 8000
```

`Restart=always`、`RestartSec=3` 负责进程退出后的恢复，`enable` 启用开机启动。
日志由 journal 收集，不再写 `backend.log`。
`history.db` 会自动初始化。线上数据库独立于本地数据库，拉取代码不会同步或清空数据。

Nginx 当前核心配置：

```nginx
root /root/1154/out;
index index.html;

location / {
    try_files $uri $uri.html $uri/ =404;
}

location /api/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

把 `deploy/nginx-api.conf` 的内容加入已有站点的 `server` 块，保留其他配置。
`proxy_pass` 末尾不要加斜杠，才能完整保留 `/api/` 路径。
修改后执行 `nginx -t && systemctl reload nginx`。
只有 `/api/` 会进入后端，`/docs`、`/redoc`、`/openapi.json` 从公网访问返回 404。

## 检查与后续更新

```bash
curl -fsS http://localhost/api/profile
curl -fsS http://127.0.0.1:8000/api/profile
ss -lntp 'sport = :8000'
systemctl --no-pager status zero-backend
systemctl is-enabled zero-backend
journalctl -u zero-backend -n 50 --no-pager
```

访问线上文字实验室做一次分析，打开历史记录；换浏览器或无痕窗口，历史应互相隔离。
关闭 SSH 窗口后再访问，后端应仍能响应。

日常发布先在本地提交并推送，然后服务器执行：

```bash
cd /root/1154
git pull --ff-only
. /root/.nvm/nvm.sh
npm ci --no-audit --no-fund                         # 前端依赖变化时
NEXT_TELEMETRY_DISABLED=1 npm run build            # 前端更新时
backend/.venv/bin/python -m pip install -r backend/requirements.txt  # 后端依赖变化时
systemctl restart zero-backend                    # 后端更新时
```

前端只改构建产物，无需重启 Nginx。修改 service 文件后，需要重新安装文件、`daemon-reload` 和 `restart`。
后端手动停启使用 `systemctl stop zero-backend` / `systemctl start zero-backend`；
`stop` 会保持停止，不会触发自动恢复。实时日志用 `journalctl -u zero-backend -f`，Ctrl+C 退出日志查看。
更新时保留 `history.db` 和 `.env`。迁移前已备份数据库、前端产物和配置，原有记录保持不变。

验证范围：公网页面和资源、同源 API、独立 Cookie 历史隔离、SQLite 数据保留、
后台进程自动恢复与手动停启、开机启动已启用、8000 公网直连不可达。
开机启动通过 systemd 的 enabled 状态确认，没有为验证而重启整台服务器。
