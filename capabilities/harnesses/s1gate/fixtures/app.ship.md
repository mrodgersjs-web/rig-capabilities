# Release record: Grok Bot clone web release (HELD at Gate-D)

- Production build: `npm run build` (next build --webpack) exit 0, 10/10 routes compiled; log at /tmp/grokbot-build.log.
- Env audit: target needs DATABASE_URL, CLERK_SECRET_KEY, NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY, OPENAI_API_KEY, INNGEST_SIGNING_KEY; each set in Vercel project settings; any change is followed by a redeploy without build cache.
- Gate-D: deploy to production and domain attach are HELD awaiting Mike's approval; no push or deploy has happened.
- Post-release check once approved: sha256 of the live / page and of the main JS chunk must differ from the previous deployment; /dashboard returns 307 signed out; /api/health returns 200 {"ok":true}.
- Rollback: promote the previous production deployment in Vercel.
- Store policy: not a mobile app store release.
