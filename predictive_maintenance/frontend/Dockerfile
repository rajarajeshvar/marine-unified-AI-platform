FROM node:20-alpine

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

# Tailwind v4 handles the build automatically, but let's build Next.js
RUN npm run build

CMD ["npm", "start"]
