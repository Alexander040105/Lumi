# API Structure Guide

## Large Project Structure
- Keep one router per domain (users, billing, reports)
- Add an api.py aggregator that registers all routers
- Use versioned prefixes like /api/v1

## Route Separation Strategies
- One file per domain
- Nested routers for sub-domains
- Group shared dependencies in app/dependencies

## Service Separation Strategies
- External integrations in their own services
- Database logic in a dedicated service module
- Keep orchestration logic in services, not routes

## Authentication Organization
- JWT verification lives in app/auth
- Dependencies provide current user context
- Protected endpoints use Depends(get_current_user)

## Flask Blueprint Equivalents
- Blueprint registration -> include_router
- Blueprint url_prefix -> include_router prefix
- Blueprint blueprint_name -> router tags

## When to Create a New Module
- When a router exceeds 150-200 lines
- When a domain needs its own schemas and services
- When an integration requires multiple endpoints
