# Holiday Or Work API

一个部署到 Vercel 的 FastAPI 服务，用 `chinese-calendar` 判断中国法定节假日、调休休息日、补班日，并返回某个月的工作日和休息日。

## 功能

- `GET /check_date/{date_str}`: 查询单天是否是工作日、是否是法定假期、是否是调休休息日、是否是补班日。
- `GET /month?year=2026&month=3`: 查询指定月份的全部日期、工作日列表、休息日列表。
- `GET /month`: 不传 `year` 和 `month` 时，默认按 `Asia/Shanghai` 时区返回当前月份。
- `GET /docs`: FastAPI 自动生成的 Swagger 文档。

## 本地启动

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.index:app --reload
```

启动后访问：

- [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- [http://127.0.0.1:8000/month](http://127.0.0.1:8000/month)

## 返回示例

`GET /check_date/2026-03-18`

```json
{
  "date": "2026-03-18",
  "is_workday": true,
  "is_rest_day": false,
  "is_weekend": false,
  "is_public_holiday": false,
  "is_in_lieu": false,
  "is_makeup_workday": false,
  "is_holiday_related_day": false,
  "holiday_name": null,
  "day_type": "workday",
  "weekday": 3,
  "day_of_week": "Wednesday"
}
```

## 部署到 Vercel

1. 把仓库推到 GitHub。
2. 在 Vercel 导入这个仓库。
3. Vercel 会自动识别 `vercel.json` 并部署 `api/index.py`。

## 自动更新说明

`chinese-calendar` 不会自己联网刷新节假日数据。这个项目用了两层处理：

1. `requirements.txt` 中把 `chinese-calendar` 设为范围版本，新的构建会安装最新可用版本。
2. `.github/workflows/refresh-vercel-deploy.yml` 会在每年 11 月 25 日到 30 日每天触发一次 Vercel Deploy Hook，强制重新部署。

你需要在 GitHub 仓库里配置一个 Secret：

- `VERCEL_DEPLOY_HOOK_URL`: 在 Vercel 项目的 Deploy Hooks 页面生成。

这样当 `chinese-calendar` 在国务院放假通知后更新版本时，Vercel 会自动重新构建并拉取新版本依赖。
