# 案卷管理系统

基于 Django + Vue 3 的案卷管理系统，支持案卷管理和分类管理功能。

## 技术栈

### 后端
- Django 4.2
- Django REST Framework
- PostgreSQL
- django-cors-headers
- django-filter

### 前端
- Vue 3
- Vite
- Element Plus
- Vue Router
- Axios

### 部署
- Docker
- Docker Compose

## 功能特性

### 案卷管理
- 案卷的增删改查
- 案卷状态管理（草稿、待审核、已通过、已驳回）
- 按分类、状态、关键词搜索
- 分页展示

### 分类管理
- 分类的增删改查
- 支持多级分类（父子分类）
- 分类树状结构展示

### 仪表盘
- 案卷总数、分类总数统计
- 状态分布统计
- 最近案卷展示
- 分类统计

## 快速开始

### 使用 Docker 部署（推荐）

1. 克隆项目
```bash
git clone <repository-url>
cd lh-20
```

2. 启动服务
```bash
docker-compose up -d
```

3. 创建超级用户
```bash
docker-compose exec backend python manage.py createsuperuser
```

4. 访问应用
- 前端：http://localhost:3000
- 后端 API：http://localhost:8000/api/
- Django Admin：http://localhost:8000/admin/

### 本地开发

#### 后端设置

1. 进入后端目录
```bash
cd backend
```

2. 创建虚拟环境并安装依赖
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. 复制环境变量文件
```bash
cp .env.example .env
```

4. 配置数据库（需要 PostgreSQL），然后执行迁移
```bash
python manage.py migrate
python manage.py createsuperuser
```

5. 启动后端服务
```bash
python manage.py runserver
```

#### 前端设置

1. 进入前端目录
```bash
cd frontend
```

2. 安装依赖
```bash
npm install
```

3. 启动开发服务器
```bash
npm run dev
```

4. 访问 http://localhost:3000

## API 接口

### 分类接口
- `GET /api/categories/` - 获取分类列表
- `POST /api/categories/` - 创建分类
- `GET /api/categories/{id}/` - 获取分类详情
- `PUT /api/categories/{id}/` - 更新分类
- `DELETE /api/categories/{id}/` - 删除分类
- `GET /api/categories/tree/` - 获取分类树
- `GET /api/categories/simple/` - 获取简化分类列表

### 案卷接口
- `GET /api/archives/` - 获取案卷列表（支持分页、筛选、搜索）
- `POST /api/archives/` - 创建案卷
- `GET /api/archives/{id}/` - 获取案卷详情
- `PUT /api/archives/{id}/` - 更新案卷
- `DELETE /api/archives/{id}/` - 删除案卷

## 项目结构

```
lh-20/
├── backend/                 # Django 后端
│   ├── archive_system/      # 项目配置
│   ├── archives/            # 案卷应用
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/                # Vue 3 前端
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── api/            # API 接口
│   │   ├── router/         # 路由配置
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md
```

## 数据库模型

### Category（分类）
- name: 分类名称
- description: 分类描述
- parent: 父分类（自关联）
- created_at: 创建时间
- updated_at: 更新时间

### Archive（案卷）
- title: 案卷标题
- description: 案卷描述
- archive_number: 案卷编号（唯一）
- category: 所属分类
- status: 状态（draft/pending/approved/rejected）
- created_at: 创建时间
- updated_at: 更新时间
- created_by: 创建人

## Git 管理

项目已配置 `.gitignore` 文件，忽略以下内容：
- Python 缓存文件
- 环境变量文件
- 数据库文件
- Node.js 依赖
- 构建产物
- IDE 配置文件

## 开发说明

### 添加新功能
1. 在 `backend/archives/models.py` 中定义新模型
2. 创建或更新序列化器 `serializers.py`
3. 创建或更新视图 `views.py`
4. 配置路由 `urls.py`
5. 在前端 `src/api/` 中添加 API 调用
6. 创建或更新页面组件

### 代码规范
- 后端遵循 PEP 8 规范
- 前端使用 ESLint（建议配置）

## 生产部署注意事项

1. 修改 `SECRET_KEY` 为安全值
2. 设置 `DEBUG=False`
3. 配置正确的 `ALLOWED_HOSTS`
4. 使用 HTTPS
5. 配置数据库备份策略
6. 使用 Gunicorn 或 uWSGI 替代 Django 开发服务器
7. 配置 Nginx 作为反向代理

## 许可证

MIT
