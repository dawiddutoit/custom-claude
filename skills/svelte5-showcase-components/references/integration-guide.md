# Integration Guide

Complete guide for extracting and using components from the Svelte 5 Showcase in your own projects.

## Table of Contents

1. [Quick Setup](#quick-setup)
2. [Component Architecture](#component-architecture)
3. [Required Dependencies](#required-dependencies)
4. [Configuration Files](#configuration-files)
5. [Copy/Paste Integration](#copypaste-integration)
6. [Common Patterns](#common-patterns)
7. [Form Integration](#form-integration)
8. [Styling Customization](#styling-customization)
9. [Troubleshooting](#troubleshooting)

---

## Quick Setup

### 1. Install Required Dependencies

```bash
# Core dependencies
npm install @sveltejs/kit svelte@^5.0.0 typescript
npm install @tanstack/svelte-query lucide-svelte zod
npm install mode-watcher svelte-copy svelte-sonner

# Development dependencies
npm install -D @tailwindcss/vite tailwindcss@4.0.0-beta.3
npm install -D bits-ui clsx tailwind-merge tailwind-variants
npm install -D formsnap sveltekit-superforms
npm install -D embla-carousel-svelte paneforge vaul-svelte
```

### 2. Configure Vite

**Critical:** Tailwind plugin MUST come before SvelteKit plugin.

```typescript
// vite.config.ts
import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [
    // CRITICAL: Tailwind MUST come before sveltekit()
    tailwindcss(),
    sveltekit()
  ]
});
```

### 3. Create Utilities

```typescript
// src/lib/utils.ts
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export type WithoutChild<T> = T extends { child?: any } ? Omit<T, 'child'> : T;
export type WithoutChildren<T> = T extends { children?: any } ? Omit<T, 'children'> : T;
export type WithoutChildrenOrChild<T> = WithoutChildren<WithoutChild<T>>;
export type WithElementRef<T, U extends HTMLElement = HTMLElement> = T & { ref?: U | null };
```

### 4. Import Tailwind in Layout

```svelte
<!-- src/routes/+layout.svelte -->
<script lang="ts">
  import '@tailwindcss/vite/client';
</script>

<slot />
```

---

## Component Architecture

### shadcn-svelte Philosophy

Components in this showcase follow the **shadcn-svelte** approach:

1. **Copy/Paste, Not NPM** - Components are copied directly into your project
2. **Full Control** - You own the code and can customize freely
3. **Headless Primitives** - Built on Bits UI for accessibility
4. **Tailwind Styling** - Uses Tailwind CSS for all styling
5. **TypeScript First** - Full type safety with strict mode

### Component Structure

```
src/lib/components/ui/
├── button/
│   └── button.svelte          # Single component
├── card/
│   ├── card.svelte           # Main wrapper
│   ├── card-header.svelte    # Subcomponent
│   ├── card-title.svelte     # Subcomponent
│   ├── card-content.svelte   # Subcomponent
│   └── card-footer.svelte    # Subcomponent
└── index.ts                   # Barrel export
```

### Barrel Exports

```typescript
// src/lib/components/index.ts
export { Button } from './ui/button';
export { Card, CardHeader, CardTitle, CardContent, CardFooter } from './ui/card';
export { Input } from './ui/input';
// ... more exports
```

**Usage:**
```svelte
<script lang="ts">
  // Import from single location
  import { Button, Card, CardHeader, Input } from '$lib/components';
</script>
```

---

## Required Dependencies

### Core Framework

| Package | Version | Purpose |
|---------|---------|---------|
| `svelte` | `^5.2.0` | Component framework (Svelte 5 runes) |
| `@sveltejs/kit` | `^2.9.0` | Full-stack framework |
| `typescript` | `^5.7.2` | Type safety (strict mode) |

### UI Primitives

| Package | Version | Purpose |
|---------|---------|---------|
| `bits-ui` | `^2.14.4` | Headless accessible components |
| `lucide-svelte` | `^0.562.0` | Icon library (1,666 icons) |
| `mode-watcher` | `^1.1.0` | Dark mode support |

### Styling

| Package | Version | Purpose |
|---------|---------|---------|
| `@tailwindcss/vite` | `^4.0.0-beta.3` | Tailwind CSS v4 (beta) |
| `tailwindcss` | `^4.0.0-beta.3` | CSS framework |
| `clsx` | `^2.1.1` | Conditional class utility |
| `tailwind-merge` | `^3.4.0` | Merge Tailwind classes |
| `tailwind-variants` | `^3.2.2` | Component variants |

### Form Handling

| Package | Version | Purpose |
|---------|---------|---------|
| `sveltekit-superforms` | `^2.29.1` | Server-side form validation |
| `formsnap` | `^2.0.1` | Form primitives |
| `zod` | `^3.24.1` | Runtime validation + types |

### Data Fetching

| Package | Version | Purpose |
|---------|---------|---------|
| `@tanstack/svelte-query` | `^5.62.3` | Server state management |

### Advanced Components

| Package | Version | Purpose |
|---------|---------|---------|
| `embla-carousel-svelte` | `^8.6.0` | Carousel component |
| `vaul-svelte` | `^1.0.0-next.7` | Drawer component |
| `paneforge` | `^1.0.2` | Resizable panels |
| `svelte-sonner` | `^1.0.7` | Toast notifications |

---

## Configuration Files

### TypeScript Config

```json
// tsconfig.json
{
  "extends": "./.svelte-kit/tsconfig.json",
  "compilerOptions": {
    "strict": true,
    "allowJs": true,
    "checkJs": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "skipLibCheck": true,
    "sourceMap": true
  }
}
```

### Path Aliases

SvelteKit automatically configures `$lib` alias:

```typescript
// Automatically available
import { Button } from '$lib/components';
import { cn } from '$lib/utils';
```

---

## Copy/Paste Integration

### Method 1: Using shadcn-svelte CLI (Recommended)

```bash
# Initialize shadcn-svelte in your project
npx shadcn-svelte@latest init

# Add specific components
npx shadcn-svelte@latest add button
npx shadcn-svelte@latest add card
npx shadcn-svelte@latest add form
```

The CLI will:
1. Install required dependencies
2. Copy component files to `src/lib/components/ui/`
3. Update barrel exports in `index.ts`

### Method 2: Manual Copy

1. **Copy component directory:**
   ```bash
   cp -r /path/to/showcase/src/lib/components/ui/button ./src/lib/components/ui/
   ```

2. **Update barrel exports:**
   ```typescript
   // src/lib/components/index.ts
   export { Button, buttonVariants } from './ui/button';
   ```

3. **Install component dependencies:**
   - Check component's imports
   - Install any missing dependencies

### Method 3: Copy from Showcase

Navigate to showcase:
```
/Users/dawiddutoit/projects/play/svelte/src/lib/components/ui/
```

Copy desired component directories to your project.

---

## Common Patterns

### Svelte 5 Runes (Required)

All components use Svelte 5 runes syntax:

```svelte
<script lang="ts">
  // ❌ Svelte 4 (DO NOT USE)
  let count = 0;
  $: doubled = count * 2;

  // ✅ Svelte 5 (REQUIRED)
  let count = $state(0);
  let doubled = $derived(count * 2);

  $effect(() => {
    console.log(count);
  });
</script>
```

### Props Pattern

```svelte
<script lang="ts">
  interface Props {
    title: string;
    count?: number;
    onUpdate?: (value: number) => void;
  }

  let { title, count = 0, onUpdate }: Props = $props();
</script>
```

### Bindable Props

```svelte
<script lang="ts">
  interface Props {
    value: string;
  }

  let { value = $bindable() }: Props = $props();
</script>

<input bind:value />
```

### Component Composition

```svelte
<script lang="ts">
  import { Card, CardHeader, CardTitle, CardContent } from '$lib/components';
</script>

<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>
    <p>Content here</p>
  </CardContent>
</Card>
```

### Tailwind Utilities

```svelte
<script lang="ts">
  import { cn } from '$lib/utils';

  interface Props {
    class?: string;
  }

  let { class: className }: Props = $props();
</script>

<div class={cn('default-classes', className)}>
  Content
</div>
```

---

## Form Integration

### Complete Form Example

**1. Create Zod Schema:**

```typescript
// src/routes/contact/schema.ts
import { z } from 'zod';

export const contactSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  message: z.string().min(10, 'Message must be at least 10 characters'),
  newsletter: z.boolean().default(false)
});

export type ContactForm = z.infer<typeof contactSchema>;
```

**2. Server-Side Load Function:**

```typescript
// src/routes/contact/+page.server.ts
import type { PageServerLoad, Actions } from './$types';
import { superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { contactSchema } from './schema';
import { fail } from '@sveltejs/kit';

export const load: PageServerLoad = async () => {
  const form = await superValidate(zod(contactSchema));
  return { form };
};

export const actions: Actions = {
  default: async ({ request }) => {
    const form = await superValidate(request, zod(contactSchema));

    if (!form.valid) {
      return fail(400, { form });
    }

    // Process form data
    console.log('Form submitted:', form.data);

    return { form };
  }
};
```

**3. Client-Side Component:**

```svelte
<!-- src/routes/contact/+page.svelte -->
<script lang="ts">
  import { superForm } from 'sveltekit-superforms';
  import { zodClient } from 'sveltekit-superforms/adapters';
  import {
    FormField,
    FormLabel,
    FormDescription,
    FormFieldErrors,
    Input,
    Textarea,
    Checkbox,
    Button
  } from '$lib/components';
  import { contactSchema } from './schema';
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();

  const { form, errors, enhance, delayed } = superForm(data.form, {
    validators: zodClient(contactSchema)
  });
</script>

<form method="POST" use:enhance class="space-y-6 max-w-2xl">
  <FormField name="name" {form}>
    {#snippet children({ value })}
      <FormLabel>Full Name</FormLabel>
      <Input bind:value={$form.name} placeholder="John Doe" />
      <FormFieldErrors />
    {/snippet}
  </FormField>

  <FormField name="email" {form}>
    {#snippet children({ value })}
      <FormLabel>Email</FormLabel>
      <FormDescription>We'll never share your email</FormDescription>
      <Input type="email" bind:value={$form.email} placeholder="you@example.com" />
      <FormFieldErrors />
    {/snippet}
  </FormField>

  <FormField name="message" {form}>
    {#snippet children({ value })}
      <FormLabel>Message</FormLabel>
      <Textarea bind:value={$form.message} rows={5} placeholder="Your message..." />
      <FormFieldErrors />
    {/snippet}
  </FormField>

  <FormField name="newsletter" {form}>
    {#snippet children({ value })}
      <div class="flex items-center space-x-2">
        <Checkbox id="newsletter" bind:checked={$form.newsletter} />
        <FormLabel for="newsletter">Subscribe to newsletter</FormLabel>
      </div>
      <FormFieldErrors />
    {/snippet}
  </FormField>

  <Button type="submit" disabled={$delayed}>
    {$delayed ? 'Submitting...' : 'Send Message'}
  </Button>
</form>
```

---

## Styling Customization

### Variant Customization

Components use `tailwind-variants` for variant management:

```typescript
// Example: Customizing button variants
import { tv, type VariantProps } from 'tailwind-variants';

export const buttonVariants = tv({
  base: 'inline-flex items-center justify-center rounded-md text-sm font-medium transition-all',
  variants: {
    variant: {
      default: 'bg-primary text-primary-foreground hover:bg-primary/90',
      destructive: 'bg-destructive text-white hover:bg-destructive/90',
      // Add custom variant
      success: 'bg-green-600 text-white hover:bg-green-700'
    },
    size: {
      default: 'h-9 px-4 py-2',
      sm: 'h-8 px-3',
      lg: 'h-10 px-6',
      // Add custom size
      xl: 'h-12 px-8 text-base'
    }
  },
  defaultVariants: {
    variant: 'default',
    size: 'default'
  }
});
```

### CSS Variable Theming

Components support CSS variable theming:

```css
/* src/app.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
    /* Add more variables */
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --primary: 217.2 91.2% 59.8%;
    --primary-foreground: 222.2 47.4% 11.2%;
    /* Add more variables */
  }
}
```

### Dark Mode Support

Use `mode-watcher` for automatic dark mode:

```svelte
<!-- src/routes/+layout.svelte -->
<script lang="ts">
  import { ModeWatcher } from 'mode-watcher';
</script>

<ModeWatcher />
<slot />
```

---

## Troubleshooting

### Common Issues

**1. Import errors after copying components**

```
Error: Cannot find module 'bits-ui'
```

**Solution:** Install missing dependencies:
```bash
npm install bits-ui
```

**2. Tailwind classes not applying**

**Solution:** Ensure Tailwind plugin comes BEFORE SvelteKit in `vite.config.ts`:
```typescript
plugins: [
  tailwindcss(),  // FIRST
  sveltekit()     // SECOND
]
```

**3. Svelte 5 runes errors**

```
Error: Reactivity is not enabled
```

**Solution:** Ensure you're using Svelte 5 syntax:
```svelte
let count = $state(0);  // NOT: let count = 0;
```

**4. Form validation not working**

**Solution:** Ensure you're using the correct adapter:
```typescript
// Server-side
import { zod } from 'sveltekit-superforms/adapters';
await superValidate(request, zod(schema));

// Client-side
import { zodClient } from 'sveltekit-superforms/adapters';
superForm(data.form, { validators: zodClient(schema) });
```

**5. Icons not showing**

**Solution:** Import icons from `lucide-svelte`:
```svelte
<script lang="ts">
  import { Mail, User, Settings } from 'lucide-svelte';
</script>

<Mail class="h-4 w-4" />
```

### Debugging Tips

1. **Check browser console** for runtime errors
2. **Run `npm run check`** for TypeScript errors
3. **Verify imports** match component exports
4. **Check dependencies** are installed
5. **Review Svelte 5 migration guide** for syntax changes

---

## Best Practices

1. **Use the CLI when possible** - `npx shadcn-svelte@latest add <component>`
2. **Keep TypeScript strict** - Don't disable strict mode
3. **Follow Svelte 5 patterns** - Use runes, not Svelte 4 syntax
4. **Customize freely** - You own the code, modify as needed
5. **Test components** - Write tests for custom behavior
6. **Document changes** - Track customizations for future reference
7. **Stay updated** - Watch for Bits UI and shadcn-svelte updates

---

## Additional Resources

- **Svelte 5 Docs:** https://svelte.dev/docs/svelte/overview
- **SvelteKit Docs:** https://svelte.dev/docs/kit/introduction
- **shadcn-svelte:** https://shadcn-svelte.com
- **Bits UI:** https://bits-ui.com
- **sveltekit-superforms:** https://superforms.rocks
- **TanStack Query:** https://tanstack.com/query/latest/docs/svelte/overview
- **Tailwind CSS v4:** https://tailwindcss.com/docs
- **Lucide Icons:** https://lucide.dev
