# ROI Calculator & AI Financial Advisor

A Flask web application that helps beginner and retail investors make sense of stock performance — pulling real-time market data and turning it into plain-language buy/hold/sell guidance powered by AI.

## Overview

Most financial tracking apps and trading platforms surface raw stock prices, news, and charts, but stop short of translating that data into a clear decision. This project fills that gap: users search a stock, the app calculates ROI over a chosen time frame, and an AI layer explains what the numbers mean and what to consider doing next.

## Target Users

- **Beginning investors** who are new to the stock market and want simple, clear ROI insights
- **Retail investors** who need a fast way to assess a position based on ROI metrics
- **Casual investors** who want on-demand financial guidance without constant portfolio monitoring

## Features

**Core (MVP)**
- Landing page with access to all sections
- Real-time and historical stock data via the Yahoo Finance API
- ROI calculation over user-selected time frames
- AI-generated financial advice (buy / hold / sell) based on ROI and performance, powered by the OpenAI ChatGPT API
- User sign-up flow (name, email, password)
- Admin tooling: compose and manage financial education articles, with visibility and edit/delete controls

**Nice to Have**
- Persistent user accounts to save stock data, preferences, and past ROI calculations
- Advanced analytics beyond ROI, including risk assessment
- Portfolio management across multiple stocks with real-time ROI and advice updates
- Personalised recommendations based on individual investment goals

**Stretch Goals**
- Real-time streaming stock price updates with live ROI recalculation
- AI-driven portfolio optimisation across a user's full holdings

## Tech Stack

`Python` · `Flask` · `Yahoo Finance API` (`yfinance`) · `OpenAI API`

## How It Works

1. A user searches for a stock on the stock search page.
2. The app pulls current and historical price data via `yfinance`.
3. ROI is calculated over the selected time frame.
4. The OpenAI API analyses the stock's performance and ROI, returning a plain-language recommendation.
5. Admins can compose and manage supporting financial education articles through a dedicated content-management panel.

## Repository Structure

```
├── app.py                  # Flask server and routes
├── templates/               # HTML templates (landing, sign-up, articles, admin)
├── static/                  # CSS/JS assets
└── README.md
```

## Next Steps

- Persist user accounts and saved calculations beyond a single session
- Add portfolio-level tracking and risk metrics
- Move from route-level sample data to live user-entered data end-to-end
- Explore real-time price streaming for live ROI updates

---
*Rose Nguyen — Bachelor of Actuarial Studies (Actuarial Risk Management and Analytics), UNSW*
