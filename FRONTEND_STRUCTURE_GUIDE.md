# Frontend Structure Guide

## Folder Layout
- src/components/ui: shadcn/ui primitives
- src/components/layout: navbar, sidebar, layout building blocks
- src/components/shared: reusable app components
- src/pages: route-level screens
- src/hooks: custom hooks
- src/services: API clients
- src/lib: utilities like cn()
- src/context: app-wide context (auth, theme)
- src/routes: router definitions
- src/styles: globals and theme
- src/layouts: route-level layout shells

## Layout Architecture
- MainLayout handles the shell and layout
- Navbar and Sidebar are layout components
- Page containers are applied at the page level

## Scaling Strategy
- Add a new page in src/pages and route it in src/routes
- Keep API calls in src/services
- Add UI primitives to src/components/ui
- Add feature-level components to src/components/shared

## Best Practices
- Keep UI primitives stateless
- Put domain logic in hooks or services
- Keep page components focused on composition
