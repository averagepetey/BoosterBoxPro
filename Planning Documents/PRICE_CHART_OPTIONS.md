# Price chart options

## Current: in-app SVG chart (no external API)

The **Price Trends** graph on the box detail page is a custom SVG chart with:

- **Smooth curve** (cubic Bezier) instead of jagged line segments
- Gradient fill under the line and dark-theme styling
- Same data source (time series from our API); no third-party chart API

No Apify or other external service is used for **rendering** the chart. Apify is used only for **data** (e.g. TCGplayer scrapers).

---

## Optional: QuickChart.io (free chart-as-image API)

If you ever want a **chart image** (e.g. for emails, reports, or static embeds) without rendering it in the frontend:

- **QuickChart.io** – free tier, no signup for basic use.
- You send a Chart.js-style config (labels + dataset) and get back a PNG/SVG URL.
- Example: `GET https://quickchart.io/chart?c={type:'line',data:{labels:['Jan 2','Jan 22'],datasets:[{label:'Floor',data:[398,703],borderColor:'#10b981',fill:true}]}}`
- Use your existing time-series data: map `date` → labels, `floor_price_usd` → dataset `data`.
- Docs: https://quickchart.io/documentation/

**When to use:** Static images, shareable links, or server-generated reports. For the interactive box detail page, the in-app SVG chart is better (no external request, smooth curve, same data).

---

## Apify and charts

**Apify** does not provide chart or graph **rendering** APIs. It runs scrapers/actors and returns data. We already use it (e.g. `tcgplayer_apify`) for **price/market data**. That data is what we feed into our chart; the chart itself is drawn in the app (or optionally via QuickChart if you want an image URL).
