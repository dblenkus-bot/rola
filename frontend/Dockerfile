FROM node:24.21.0-alpine AS dependencies
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM dependencies AS development
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev"]

FROM dependencies AS build
COPY . .
ARG VITE_API_BASE_URL
ARG VITE_SENTRY_DSN
ARG VITE_PAYPAL_CLIENT_ID
RUN npm run build

FROM nginx:1.30.5-alpine AS production
COPY --from=build /app/dist /usr/share/nginx/html
COPY docker/default.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
