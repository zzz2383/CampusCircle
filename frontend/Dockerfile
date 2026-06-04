# 阶段一：构建前端
FROM node:22-alpine as builder

WORKDIR /app

# 复制依赖文件并安装
COPY frontend/package*.json ./
RUN npm ci

# 复制所有源码
COPY frontend/ ./

# 修复所有可执行文件的权限（关键：在 COPY 之后执行）
RUN chmod -R +x node_modules/.bin

# 构建
RUN npm run build

# 阶段二：Nginx 服务
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]