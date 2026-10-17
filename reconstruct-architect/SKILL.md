---
name: reconstruct-architect
description: >-
  Plans the stack, database schema, API and build order for a rebuild, from
  the recon map reconstruct-recon wrote. Uses evidence-backed data shapes
  where REA found them, picks boring managed tech otherwise, and orders the
  build as a thin vertical slice first. Use when the user says "plan the
  rebuild", "what stack", "design the database", "write the schema", "plan the
  API", or after /reconstruct-recon.
---

# reconstruct-architect

Reads `reconstruct/scope.md`, `recon.md` and `features.csv`. Writes
`reconstruct/architecture.md` (template: architecture.md in this folder) and
the schema as `reconstruct/schema.sql` or the first migration.

No recon map: stop and run `/reconstruct-recon`.

## Step 1: the stack

Use the stack the user or their team already runs. Otherwise:

| layer | default |
| --- | --- |
| web | Next.js (App Router) + TypeScript |
| mobile | SwiftUI or Expo |
| database | Postgres (managed) |
| ORM | Drizzle or Prisma |
| auth | the platform's auth, or Auth.js |
| payments | Stripe Checkout + Billing |
| email | Resend or Postmark |
| jobs | a managed cron / queue |

One line of why per choice. One database. The rebuild needs the original's
features, not its architecture, even when REA showed you that architecture.

## Step 2: the schema

Start from the data model in `recon.md`. Rows with `observed` tier B evidence
are the strongest input. Match their shapes and constraints, written fresh.
`inferred` and `guess` rows are design decisions: say so in a comment.

Every table: uuid id, `created_at`, `updated_at`, an owner column, foreign keys
with a decided `on delete`, indexes on foreign keys and filter/sort columns,
check constraints for status fields, `timestamptz` in UTC, money as integer
cents plus currency, and the access rule (row level security or one
authorization check per query). Hard invariants the recon found (no double
booking, unique slugs) are database constraints, not UI checks.

## Step 3: the API

One table per flow: `method path | does | who | input | output | flow`. Plus
webhooks in and out, and jobs with their schedule.

A third party's private endpoints are never called, proxied or mirrored, even
when a capture showed them. If the target is our own product, reusing its real
API is a choice, so write it down.

## Step 4: the parts that bite

A line on each that applies: time zones, idempotency, races, rate limits, file
limits, search, realtime, offline, deliverability, multi-tenancy, deletion.
Add any edge case REA surfaced (a retry loop, a limit constant, an error
branch) with its Evidence ID.

## Step 5: build order

1. **Vertical slice**: the core loop end to end, ugly.
2. **Must-haves** from `features.csv`, by area. Any must-have still at
   `guess` confidence gets its probe first.
3. **Should-haves**, then could-haves.

Each milestone lists its screens (S-IDs), tables and routes.

## Output

`architecture.md`, the schema, and a summary: stack in one line, table count,
route count, the three riskiest parts, and the next step: `/reconstruct-build`.
