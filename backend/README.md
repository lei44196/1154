# 模块 5.4 · FastAPI 后端

`main.py` 定义 API，uvicorn 负责监听端口和运行应用。
`fastapi dev` 是开发用快捷命令，会启动 uvicorn 并开启代码修改后自动重载。

## Windows 本地运行

在项目根目录打开 PowerShell，首次安装或重新创建环境时执行：

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
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

这是 5.4 的本地开发运行方式。对公网发布和常驻运行将在部署章节处理。

## 接口与文档

- `http://127.0.0.1:8000/api/profile`：GET，返回主页标题和副标题。
- `http://127.0.0.1:8000/docs`：自动生成的交互文档，可以展开接口，点击 Try it out 和 Execute 发请求。
- `http://127.0.0.1:8000/openapi.json`：机器可读的接口约定。
- `POST /api/analyze`：请求体为 `{"text": "今天的风很轻"}`，返回原文及占位分析结果。

分析接口的返回示例：

```json
{
  "text": "今天的风很轻",
  "score": 0.5,
  "label": "偏平静",
  "pinyin": "（模块 6 再说）"
}
```

PowerShell 测试：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/profile

$body = @{ text = "今天的风很轻" } | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:8000/api/analyze -Method Post -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($body))
```

在 `/docs` 中分别提交正确的 `text`、错误的 `txt` 字段或数字类型，观察 200 和 422 的区别。
不存在的路径自动返回 JSON 404；后端代码异常会返回 500，错误原因和代码行号在服务端终端的 traceback 中。

如果 `/docs` 页面空白，检查其 CDN 资源加载情况；接口和 `/openapi.json` 可以单独验证。

## 依赖与章节范围

按课件安装 `fastapi[standard]`，并将虚拟环境中的依赖版本记录在 `requirements.txt`。
`.venv/`、`__pycache__/` 和 Python 缓存文件不提交到 Git。

本章分析值为固定占位。前端暂时保持原样，5.5 接入请求与 CORS，模块 6 再替换真实算法。
