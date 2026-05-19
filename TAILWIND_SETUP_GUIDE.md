# Tailwind Setup Guide

## What Tailwind Does
Tailwind is a utility-first CSS framework. You compose styles with small utility classes instead of writing large custom CSS files.

## Installed Packages
- tailwindcss (v4)
- @tailwindcss/vite
- @tailwindcss/postcss
- postcss
- autoprefixer
- tailwindcss-animate

Install (from react-frontend/):

- npm install

## Config Files
- tailwind.config.cjs: content scanning, theme tokens, dark mode
- vite.config.js: Tailwind v4 Vite plugin
- postcss.config.cjs: Tailwind v4 PostCSS plugin
- src/styles/globals.css: base styles and CSS variables

## File Structure
- src/styles/globals.css is the only global stylesheet
- Components rely on Tailwind classes and CSS variables

## Utility Workflow
- Use Tailwind classes for layout, spacing, typography, and color
- Use component wrappers (Card, Button, Input) for consistency
- Keep custom CSS inside @layer blocks in globals.css

## Responsive Design
Use breakpoint prefixes:
- sm: min-width 640px
- md: min-width 768px
- lg: min-width 1024px
- xl: min-width 1280px

Example:
- className="grid gap-6 md:grid-cols-2 lg:grid-cols-3"

## Theme Customization
- Tokens live in CSS variables in globals.css
- Tailwind theme uses those variables for colors and radius
- Update the CSS variables to change the entire system

## Best Practices
- Prefer component composition over repeating long class lists
- Keep layout utilities in globals.css for reuse
- Use semantic wrapper classes like page-container and stack
- Avoid inline styles unless absolutely necessary

## Troubleshooting
- If classes do not apply, confirm tailwind.config.cjs content paths
- Restart Vite after changing Tailwind config
- Ensure globals.css is imported in src/main.jsx
