# Use the official Bun image
FROM oven/bun:1.3.6 AS base
WORKDIR /app

# Stage 1: Dependencies
FROM base AS deps
COPY package.json bun.lock ./

RUN bun install --frozen-lockfile

# Stage 2: Development
# This stage keeps the dev dependencies and runs the dev server
FROM deps AS dev
COPY . .
# Expose the SvelteKit dev port and the HMR port
EXPOSE 5173
CMD ["bun", "--bun", "run", "dev", "--host", "0.0.0.0"]

# Stage 3: Build
FROM deps AS build
COPY . .
RUN bun run build

# Stage 4: Production
# Only copy the build output and production dependencies
FROM base AS prod
COPY --from=build /app/build ./build
COPY --from=build /app/node_modules ./node_modules
COPY package.json .

ENV NODE_ENV=production
EXPOSE 3000
CMD ["bun", "./build/index.js"]