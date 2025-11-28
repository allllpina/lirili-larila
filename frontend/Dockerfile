# --- Етап 1: Збірка (Builder) ---
FROM node:22-alpine as builder

WORKDIR /app

# Копіюємо файли залежностей
COPY package.json package-lock.json ./

# Встановлюємо залежності
RUN npm ci

# Копіюємо весь код
COPY . .

# Збираємо проект (створюється папка dist)
RUN npm run build

# --- Етап 2: Запуск (Runner) ---
FROM nginx:alpine

# Копіюємо збілджені файли з етапу builder в папку Nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Копіюємо наш конфіг Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Відкриваємо порт 80 (внутрішній для контейнера)
EXPOSE 80

# Запускаємо Nginx
CMD ["nginx", "-g", "daemon off;"]