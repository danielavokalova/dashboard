# Flush Caches

<!-- tags: cache, flush, refresh, clear, performance, search results -->

GOL IBE caches fare and availability data to speed up search results. Use Flush Caches when you need to force a fresh data load.

## When to use

- After changing markup or fare rules (to see updated prices immediately)
- After enabling a new carrier or connector
- When search results seem outdated

## How to flush

1. Go to **Code Lists → Flush Caches**.
2. Select the cache type:
   - **Fare cache** – clears cached flight prices
   - **Availability cache** – clears seat availability data
   - **All caches** – full refresh
3. Click **Flush now**.

> ⚠️ Flushing all caches may slow down the first search after flushing as data reloads from the GDS.
