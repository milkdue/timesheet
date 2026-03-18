# 初始化

初始化一个 python fastapi项目，我需要使用 chinesecalendar 去获取这个月的哪些天是工作日哪些天是休息日

### 1. 自动更新的机制
`chinesecalendar` 库的开发者通常会在每年 11 月底（国务院发布明年放假通知后的 24 小时内）更新库的版本。
* **它不会“自发”联网更新：** 如果你把代码部署到云端就不管了，它存储的是当前的逻辑。
* **如何实现自动更新：** 你需要配置你的云端环境，在每年 11 月执行一次 `pip install --upgrade chinese-calendar`。或者使用 **Docker** 重新构建镜像，确保拉取的是最新版本。

---

### 2. 云端接口推荐方案 (Python + FastAPI)
你可以使用极简的 **FastAPI** 框架写一个接口，部署在vercel上

#### **核心代码示例：**
```python
from fastapi import FastAPI
import datetime
from chinese_calendar import is_workday, get_holiday_detail

app = FastAPI()

@app.get("/check_date/{date_str}")
def check_date(date_str: str):
    # 输入格式如: 2026-03-18
    t_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    
    # 获取详细信息
    is_work = is_workday(t_date)
    holiday_status, holiday_name = get_holiday_detail(t_date)
    
    return {
        "date": date_str,
        "is_workday": is_work,          # 是否需要生成单据（补班也为True）
        "is_holiday": holiday_status,   # 是否是法定节假日/调休假
        "holiday_name": holiday_name,   # 节日名称（如春节）
        "day_of_week": t_date.strftime('%A')
    }
```
