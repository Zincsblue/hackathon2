---
name: frontend-skill
description: Build responsive pages, reusable components, layouts, and styling. Use for UI implementation.
---

# Frontend Component Design

## Instructions

1. **Component Architecture**
   - Functional components
   - Prop validation (Interfaces)
   - Modular file structure

2. **Layout & Styling**
   - Flexbox/Grid systems
   - Responsive breakpoints
   - CSS modules or Tailwind classes

3. **Interaction**
   - Event handlers
   - State hooks (useState, useEffect)
   - Loading states

## Best Practices
- Use semantic HTML tags
- Ensure WCAG accessibility
- Optimize images and assets
- Keep components small and focused

## Example Structure
```jsx
export default function Card({ title, image, children }) {
  return (
    <article className="card-container">
      <img src={image} alt={title} className="card-img" />
      <div className="card-content">
        <h2 className="text-xl font-bold">{title}</h2>
        {children}
      </div>
    </article>
  );
}