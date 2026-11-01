# 模块 7.1 · 配置与全栈部署

`main.py` 定义 API 和分析业务，`storage.py` 负责 SQLite 读写，uvicorn 负责监听端口和运行应用。
`fastapi dev` 是开发用快捷命令，会启动 uvicorn 并开启代码修改后自动重载。

## Windows 本地运行

在项目根目录打开 PowerShell，首次安装或重新创建环境时执行：

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
```

启动后端：

```powershell
cd backend
$env:PYTHONUTF8 = "1"
.\.venv\Scripts\fastapi.exe dev main.py
```

以上写法直接使用虚拟环境里的程序，无须修改 PowerShell 的执行策略。
UTF-8 设置用于兼容命令行的中文和表情符号输出，避免旧终端默认 GBK 编码时报错。
保持终端运行，使用 Ctrl+C 停止服务。前端开发服务使用另一个终端运行 `npm run dev`。

课件中 uvicorn 的等价写法（任选一种启动，不要同时占用 8000 端口）：

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

## Linux 环境

```bash
cd /root/1154/backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/fastapi dev main.py
```

这是本地开发运行方式。公网发布和后台运行见项目根目录 README 的部署流程。

## 环境配置

首次运行先复制 `backend/.env.example` 为 `backend/.env`。本地填写
`ALLOWED_ORIGINS=http://localhost:3000`；线上填写实际前端地址，例如
`ALLOWED_ORIGINS=http://123.57.184.86`，多个地址用英文逗号分隔。

`python-dotenv` 读取 `main.py` 同目录的 `.env`；已有进程环境变量优先于文件。
修改后需要重启后端。真实配置不提交，`.env.example` 随代码提交。

## 接口与文档

- `http://127.0.0.1:8000/api/profile`：GET，返回主页文案。
- `http://127.0.0.1:8000/docs`：自动生成的交互文档，可以展开接口，点击 Try it out 和 Execute 发请求。
- `http://127.0.0.1:8000/openapi.json`：机器可读的接口约定。
- `POST /api/analyze`：请求体为 `{"text": "我特别喜欢这部电影"}`，返回原文、情感分数、标签与带声调的拼音。
- `GET /api/history`：只返回当前 Cookie 会话的最近 10 条分析记录，新的排在前面，并附带自增 `id`；新访客返回 `[]`。
- `GET /api/history?limit=2`：指定返回条数，允许 1～100，默认 10。

分析接口的返回示例：

```json
{
  "text": "我特别喜欢这部电影",
  "score": 0.95,
  "label": "偏积极",
  "pinyin": "wǒ tè bié xǐ huān zhè bù diàn yǐng",
  "created_at": "2026-11-01T02:00:00+00:00"
}
```

PowerShell 测试：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/profile
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-RestMethod http://localhost:8000/api/history -WebSession $session

$body = @{ text = "今天的风很轻" } | ConvertTo-Json
Invoke-RestMethod http://localhost:8000/api/analyze -Method Post -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($body)) -WebSession $session
Invoke-RestMethod http://localhost:8000/api/history -WebSession $session
```

在 `/docs` 中分别提交正确的 `text`、错误的 `txt` 字段或数字类型，观察 200 和 422 的区别。
不存在的路径自动返回 JSON 404；后端代码异常会返回 500，错误原因和代码行号在服务端终端的 traceback 中。

如果 `/docs` 页面空白，检查其 CDN 资源加载情况；接口和 `/openapi.json` 可以单独验证。

## 6.1：安装、验证第三方库

在项目根目录安装或更新本章新增依赖：

```powershell
backend\.venv\Scripts\python.exe -m pip install pypinyin snownlp
```

想按课件体验 REPL，可运行 `backend\.venv\Scripts\python.exe`，然后逐行输入以下代码（不要输入文档里的 `>>>` 提示符）：

```python
from pypinyin import lazy_pinyin, Style
lazy_pinyin("重庆", style=Style.TONE)
lazy_pinyin("重要", style=Style.TONE)
from snownlp import SnowNLP
SnowNLP("我特别喜欢这部电影").sentiments
SnowNLP("太失望了，再也不来了").sentiments
exit()
```

已验证「重庆」读 `chóng qìng`、「重要」读 `zhòng yào`。
新增依赖版本和现有 FastAPI 环境一起记录在 `requirements.txt`。
`.venv/`、`__pycache__/` 和 Python 缓存文件不提交到 Git。

## 6.2：替换分析实现

- 使用 `round(SnowNLP(text).sentiments, 2)` 计算分数。
- 分数 `>= 0.6` 为「偏积极」，`<= 0.4` 为「偏消极」，其余为「中性」。
- 使用 `" ".join(lazy_pinyin(text, style=Style.TONE))` 生成拼音，非汉字原样保留。
- 空字符串或只有空白的输入返回 422，避免 SnowNLP 的空文本异常。
- `/api/analyze` 的地址、POST 方法和原有四个成功响应字段保持原样，前端沿用 5.5 的请求与显示逻辑；6.3 在此基础上追加 `created_at` 字段。

在文字实验室输入课件示例，可得到：

| 文本 | score | label |
| --- | --- | --- |
| 我特别喜欢这部电影 | 0.95 | 偏积极 |
| 今天的风很轻，适合把想法写下来 | 0.95 | 偏积极 |
| 太失望了，再也不来了 | 0.00 | 偏消极 |

模型在本地运行，不调用云端 API。SnowNLP 对中性陈述和反讽可能判断不准，分数不是客观标准。

## 6.3 到 6.5：存储层演进

6.3 使用 JSON 文件保存历史；6.5 先把存储代码拆到 `storage.py`，验证行为不变，再将存储实现替换为 SQLite。
现在每次有效分析会把五个分析字段写入 `backend/history.db`：原文、分数、标签、拼音和 `created_at`，数据库另生成自增主键 `id`，并用内部 `session_id` 标记归属。
时间使用 UTC，末尾带 `+00:00`；显示时再转换为用户本地时区。上面的时间戳是格式示例。

SQLite 由 Python 标准库 `sqlite3` 提供，无需再安装第三方依赖。
数据库固定在 `storage.py` 同级目录；`main.py` 加载时调用 `init_db()`，用 `IF NOT EXISTS` 确保表和索引存在。
数据库及其日志文件是运行时数据，已加入 `.gitignore`，不随源码提交。

两个文件的边界：

- `main.py`：保留请求校验、情感和拼音计算、UTC 时间戳；识别 Cookie 后，调用 `save_record(sid, result)` 存档、`get_history(sid, limit)` 读历史。
- `storage.py`：提供连接、建表、保存和查询；所有 SQL 数据值使用 `?` 参数，不拼接用户输入。
- 查询使用 `WHERE session_id = ? ORDER BY created_at DESC, id DESC LIMIT ?`，时间相同的记录按较新的 `id` 排前。
- `init_db()` 创建 `idx_history_session_created` 组合索引，每次启动重复执行也不会清空已有数据。

按课件验证：

1. 启动后端，访问 `/api/history`；尚未分析过时应为 `[]`。
2. 用文字实验室或 `/docs` 分析两三句话，再查看 `/api/history`。
3. 用 DB Browser 等 SQLite 工具打开 `backend/history.db`，查看 `history` 表、自增 `id`、`session_id` 和组合索引。
4. 停止、重启后端，再读取历史，记录仍然存在。
5. 保存超过 10 条后，接口只返回最新 10 条，数据库仍保留全部记录。

旧的 `history.json` 已不再读写；如本地曾有该文件，保留原件，本次不自动导入或删除。

## 6.6：Cookie 会话与历史弹窗

首次请求分析或历史接口时，后端生成随机 UUID，使用 `session_id` Cookie 交给浏览器保管。
Cookie 属性为 `HttpOnly`、`SameSite=Lax`、`Path=/`，有效期 30 天；后续请求复用同一个编号。
会话编号用于数据库筛选，不加入分析或历史的 JSON 响应。

跨源联调时两端都要允许凭证：后端 CORS 从 `.env` 的 `ALLOWED_ORIGINS` 读取明确的前端源并启用 `allow_credentials=True`；前端分析和历史请求带 `credentials: "include"`。
主页文案接口不识别访客，无需携带 Cookie。

前端使用根目录 `.env.local` 的 `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`，浏览器访问 `http://localhost:3000`。
本地联调统一使用 `localhost`，避免前端用 `localhost`、API 却用 `127.0.0.1` 导致 Cookie 的站点不一致。

文字实验室结果卡右上角新增「历史记录」按钮，点击后才读取自己的历史；弹窗显示浏览器本地时间，支持关闭按钮、Esc 和点击遮罩关闭，并区分加载中、空记录和请求失败。

验证隔离：

1. 普通窗口分析一句话，打开历史查看。
2. 无痕窗口或另一个浏览器访问同一前端，直接打开历史，应为空。
3. 在第二个浏览器分析不同的文字，两个浏览器应各看各的。
4. 重启后端，同一浏览器仍能读取自己的记录；清除 Cookie 后会作为新访客。

已有 6.5 数据库会自动添加 `session_id` 列并替换索引，旧记录保留为 `NULL`，不分配给任何新会话。升级前备份在 `backend/backups/`，已加入 Git 忽略规则。
这是一套匿名浏览器会话，不是注册登录；换浏览器、清 Cookie 或 Cookie 过期后，原记录仍在数据库中，但新会话无法读取。
