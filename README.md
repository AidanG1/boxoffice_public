# Box Office

An exploratory box-office data and prediction project. It includes a Python data pipeline and a Svelte/Tauri application for browsing results.

## Configuration

Copy `.env.example` to `.env` and set only the credentials needed for the part of the project you run. `.env` files are intentionally ignored and must not be committed.

The Python pipeline requires the Supabase service credential only for database-writing tasks. The web application uses a Supabase URL and anon key, which must be protected by appropriate Row Level Security policies.

## Before contributing

Keep API keys and service credentials in environment variables. Do not add generated build output, databases, or source-site data dumps to Git.
