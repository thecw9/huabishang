# build stage
FROM node:lts-alpine AS build-stage
WORKDIR /app
ENV TZ=Asia/Shanghai
COPY package*.json ./
RUN npm --registry https://registry.npmmirror.com/ install
COPY . .
RUN npm run build


# production stage
FROM nginx:stable-alpine AS production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf
EXPOSE 5173
CMD ["nginx", "-g", "daemon off;"]
