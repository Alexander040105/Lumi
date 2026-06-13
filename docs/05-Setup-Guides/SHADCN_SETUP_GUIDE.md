# shadcn/ui Setup Guide

## How shadcn/ui Works
shadcn/ui is a component generator. It copies component code into your project so you fully own the source.

## Config File
components.json controls:
- where components are generated
- alias paths
- Tailwind config and CSS file locations

## Adding New Components
From react-frontend/:

- npx shadcn-ui@latest add button
- npx shadcn-ui@latest add card

Dependencies are already listed in package.json. Run npm install to sync.

Components will be placed in src/components/ui.

## Theme and Dark Mode
- Theme tokens are defined in src/styles/globals.css
- Dark mode is toggled by adding the dark class to html
- ThemeToggle handles switching and persistence

## Customizing Components
- Edit the component files in src/components/ui
- Keep primitives small and composable
- Wrap design decisions in utility classes and tokens

## Component Ownership
All generated files are local to the repo. You can refactor freely without losing changes.

## Troubleshooting
- If aliases fail, confirm jsconfig.json and Vite alias
- If styles look off, confirm globals.css and Tailwind config
