# Quick Reference Card

Fast lookup guide for the most commonly used components.

## Most Popular Components

### Button
```svelte
import { Button } from '$lib/components';

<Button>Click me</Button>
<Button variant="destructive">Delete</Button>
<Button variant="outline">Cancel</Button>
```

### Card
```svelte
import { Card, CardHeader, CardTitle, CardContent } from '$lib/components';

<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>Content</CardContent>
</Card>
```

### Input
```svelte
import { Input, Label } from '$lib/components';

<Label for="email">Email</Label>
<Input id="email" type="email" bind:value={email} />
```

### Form Field
```svelte
import { FormField, FormLabel, Input, FormFieldErrors } from '$lib/components';

<FormField name="email" {form}>
  {#snippet children({ value })}
    <FormLabel>Email</FormLabel>
    <Input bind:value={$form.email} />
    <FormFieldErrors />
  {/snippet}
</FormField>
```

### Dialog
```svelte
import { Dialog, DialogTrigger, DialogContent } from '$lib/components';

<Dialog bind:open>
  <DialogTrigger><Button>Open</Button></DialogTrigger>
  <DialogContent>Content</DialogContent>
</Dialog>
```

### Select
```svelte
import { Select, SelectTrigger, SelectContent, SelectItem } from '$lib/components';

<Select bind:value={selected}>
  <SelectTrigger>Select...</SelectTrigger>
  <SelectContent>
    <SelectItem value="1">Option 1</SelectItem>
    <SelectItem value="2">Option 2</SelectItem>
  </SelectContent>
</Select>
```

### Tabs
```svelte
import { Tabs, TabsList, TabsTrigger, TabsContent } from '$lib/components';

<Tabs>
  <TabsList>
    <TabsTrigger value="tab1">Tab 1</TabsTrigger>
    <TabsTrigger value="tab2">Tab 2</TabsTrigger>
  </TabsList>
  <TabsContent value="tab1">Content 1</TabsContent>
  <TabsContent value="tab2">Content 2</TabsContent>
</Tabs>
```

### Toast (Sonner)
```svelte
import { toast } from 'svelte-sonner';
import { Toaster } from '$lib/components';

<!-- In layout -->
<Toaster />

<!-- Trigger toast -->
<Button onclick={() => toast.success('Saved!')}>Save</Button>
```

## Component Categories Map

**Need a button?** → `Button` (primitives)
**Need a form?** → `Form Field`, `Input`, `Textarea`, `Checkbox`, `Select` (primitives)
**Need validation?** → Use `sveltekit-superforms` + `Zod` + `FormField` components
**Need a modal?** → `Dialog` or `Drawer` (overlays)
**Need navigation?** → `Tabs`, `Breadcrumb`, `Pagination` (navigation)
**Need a notification?** → `Sonner` toast (feedback)
**Need a data table?** → `Table` (data display)
**Need a dropdown?** → `Select` or `Dropdown Menu` (primitives)
**Need icons?** → `lucide-svelte` package

## Installation Quick Commands

```bash
# Most common components
npx shadcn-svelte@latest add button
npx shadcn-svelte@latest add card
npx shadcn-svelte@latest add input
npx shadcn-svelte@latest add form
npx shadcn-svelte@latest add dialog
npx shadcn-svelte@latest add select
npx shadcn-svelte@latest add tabs
npx shadcn-svelte@latest add table

# Install all at once
npx shadcn-svelte@latest add button card input form dialog select tabs table
```

## Common Patterns Cheat Sheet

### Svelte 5 State
```svelte
let count = $state(0);
let doubled = $derived(count * 2);
$effect(() => console.log(count));
```

### Props
```svelte
interface Props {
  title: string;
  count?: number;
}
let { title, count = 0 }: Props = $props();
```

### Bindable
```svelte
let { value = $bindable() }: Props = $props();
```

### Class Merging
```svelte
import { cn } from '$lib/utils';
<div class={cn('default-class', className)}>
```

### Icon Usage
```svelte
import { Mail } from 'lucide-svelte';
<Button><Mail class="mr-2 h-4 w-4" />Email</Button>
```

## Showcase Locations

**Components:** `/Users/dawiddutoit/projects/play/svelte/src/lib/components/ui/`
**Examples:** `/Users/dawiddutoit/projects/play/svelte/src/routes/showcase/`
**Utils:** `/Users/dawiddutoit/projects/play/svelte/src/lib/utils.ts`

## Dependency Quick Install

```bash
# Minimum viable setup
npm install svelte@^5 @sveltejs/kit typescript
npm install -D @tailwindcss/vite tailwindcss
npm install bits-ui clsx tailwind-merge tailwind-variants lucide-svelte

# Add forms
npm install sveltekit-superforms formsnap zod

# Add data fetching
npm install @tanstack/svelte-query

# Add notifications
npm install svelte-sonner

# Add advanced components
npm install embla-carousel-svelte vaul-svelte paneforge
```

## Troubleshooting Quick Fixes

**Import errors?** → Install missing dependencies
**Tailwind not working?** → Check plugin order in vite.config.ts
**Runes errors?** → Use Svelte 5 syntax ($state, $derived)
**Form validation broken?** → Check adapter (zod vs zodClient)
**Icons not showing?** → Import from lucide-svelte
**TypeScript errors?** → Enable strict mode in tsconfig.json

## Component Count by Category

- Primitives: 24 components
- Navigation: 6 components
- Data Display: 6 components
- Overlays: 5 components
- Feedback: 2 components
- Layout: 2 components
- Custom: 4 components

**Total: 49 components**
