# Component Examples

Comprehensive examples demonstrating usage patterns for all 49 components in the Svelte 5 Showcase.

## Table of Contents

- [Primitives (24 components)](#primitives)
- [Navigation (6 components)](#navigation)
- [Data Display (6 components)](#data-display)
- [Overlays (5 components)](#overlays)
- [Feedback (2 components)](#feedback)
- [Layout (2 components)](#layout)
- [Custom Components (4 components)](#custom-components)

---

## Primitives

### Alert

**File Location:** `/Users/dawiddutoit/projects/play/svelte/src/lib/components/ui/alert/`

**Usage:**
```svelte
<script lang="ts">
  import { Alert, AlertTitle, AlertDescription } from '$lib/components/ui/alert';
  import { Terminal } from 'lucide-svelte';
</script>

<Alert>
  <Terminal class="h-4 w-4" />
  <AlertTitle>Heads up!</AlertTitle>
  <AlertDescription>
    You can add components to your app using the CLI.
  </AlertDescription>
</Alert>

<!-- Destructive variant -->
<Alert variant="destructive">
  <AlertTitle>Error</AlertTitle>
  <AlertDescription>
    Your session has expired. Please log in again.
  </AlertDescription>
</Alert>
```

**Props:**
- `variant`: `'default'` | `'destructive'`

### Badge

**File Location:** `/Users/dawiddutoit/projects/play/svelte/src/lib/components/ui/badge/`

**Usage:**
```svelte
<script lang="ts">
  import { Badge } from '$lib/components/ui/badge';
</script>

<Badge>Default</Badge>
<Badge variant="secondary">Secondary</Badge>
<Badge variant="destructive">Destructive</Badge>
<Badge variant="outline">Outline</Badge>
```

**Props:**
- `variant`: `'default'` | `'secondary'` | `'destructive'` | `'outline'`

### Button

**File Location:** `/Users/dawiddutoit/projects/play/svelte/src/lib/components/ui/button/`

**Usage:**
```svelte
<script lang="ts">
  import { Button } from '$lib/components/ui/button';
  import { Mail, Loader2 } from 'lucide-svelte';
</script>

<!-- Basic button -->
<Button>Click me</Button>

<!-- Variants -->
<Button variant="destructive">Delete</Button>
<Button variant="outline">Cancel</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="link">Link</Button>

<!-- Sizes -->
<Button size="sm">Small</Button>
<Button size="default">Default</Button>
<Button size="lg">Large</Button>

<!-- With icons -->
<Button>
  <Mail class="mr-2 h-4 w-4" />
  Login with Email
</Button>

<!-- Loading state -->
<Button disabled>
  <Loader2 class="mr-2 h-4 w-4 animate-spin" />
  Please wait
</Button>

<!-- As link -->
<Button href="/dashboard">Go to Dashboard</Button>
```

**Props:**
- `variant`: `'default'` | `'destructive'` | `'outline'` | `'secondary'` | `'ghost'` | `'link'`
- `size`: `'sm'` | `'default'` | `'lg'` | `'icon'` | `'icon-sm'` | `'icon-lg'`
- `disabled`: `boolean`
- `href`: `string` (renders as `<a>` tag)

### Card

**File Location:** `/Users/dawiddutoit/projects/play/svelte/src/lib/components/ui/card/`

**Usage:**
```svelte
<script lang="ts">
  import {
    Card,
    CardHeader,
    CardTitle,
    CardDescription,
    CardContent,
    CardFooter,
    CardAction
  } from '$lib/components/ui/card';
  import { Button } from '$lib/components/ui/button';
</script>

<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card description goes here</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Card content with any elements you need.</p>
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>

<!-- With action button in header -->
<Card>
  <CardHeader>
    <div class="flex items-center justify-between">
      <div>
        <CardTitle>Notifications</CardTitle>
        <CardDescription>You have 3 unread messages</CardDescription>
      </div>
      <CardAction>
        <Button variant="ghost" size="icon">...</Button>
      </CardAction>
    </div>
  </CardHeader>
  <CardContent>
    <!-- Content here -->
  </CardContent>
</Card>
```

### Checkbox

**File Location:** `/Users/dawiddutoit/projects/play/svelte/src/lib/components/ui/checkbox/`

**Usage:**
```svelte
<script lang="ts">
  import { Checkbox } from '$lib/components/ui/checkbox';
  import { Label } from '$lib/components/ui/label';

  let checked = $state(false);
</script>

<div class="flex items-center space-x-2">
  <Checkbox id="terms" bind:checked />
  <Label for="terms">Accept terms and conditions</Label>
</div>

<!-- With disabled state -->
<div class="flex items-center space-x-2">
  <Checkbox id="disabled" disabled />
  <Label for="disabled">Disabled checkbox</Label>
</div>
```

**Props:**
- `checked`: `boolean`
- `disabled`: `boolean`
- `id`: `string`

### Input

**File Location:** `/Users/dawiddutoit/projects/play/svelte/src/lib/components/ui/input/`

**Usage:**
```svelte
<script lang="ts">
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';

  let email = $state('');
</script>

<div class="space-y-2">
  <Label for="email">Email</Label>
  <Input id="email" type="email" placeholder="you@example.com" bind:value={email} />
</div>

<!-- File input -->
<Input type="file" />

<!-- Disabled -->
<Input placeholder="Disabled input" disabled />
```

**Props:**
- `type`: Standard HTML input types
- `placeholder`: `string`
- `disabled`: `boolean`
- `value`: `string` (bindable)

### Select

**File Location:** `/Users/dawiddutoit/projects/play/svelte/src/lib/components/ui/select/`

**Usage:**
```svelte
<script lang="ts">
  import {
    Select,
    SelectTrigger,
    SelectContent,
    SelectItem,
    SelectGroup,
    SelectLabel,
    SelectSeparator
  } from '$lib/components/ui/select';

  let selected = $state('apple');
</script>

<Select bind:value={selected}>
  <SelectTrigger>
    <span>Select a fruit</span>
  </SelectTrigger>
  <SelectContent>
    <SelectGroup>
      <SelectLabel>Fruits</SelectLabel>
      <SelectItem value="apple">Apple</SelectItem>
      <SelectItem value="banana">Banana</SelectItem>
      <SelectItem value="orange">Orange</SelectItem>
    </SelectGroup>
    <SelectSeparator />
    <SelectGroup>
      <SelectLabel>Vegetables</SelectLabel>
      <SelectItem value="carrot">Carrot</SelectItem>
      <SelectItem value="potato">Potato</SelectItem>
    </SelectGroup>
  </SelectContent>
</Select>
```

### Form Components

**File Location:** `/Users/dawiddutoit/projects/play/svelte/src/lib/components/ui/form/`

**Usage with sveltekit-superforms:**
```svelte
<script lang="ts">
  import { superForm } from 'sveltekit-superforms/client';
  import { z } from 'zod';
  import {
    FormField,
    FormLabel,
    FormDescription,
    FormFieldErrors,
    Input,
    Textarea,
    Button
  } from '$lib/components';

  const schema = z.object({
    email: z.string().email(),
    name: z.string().min(2),
    bio: z.string().max(500).optional()
  });

  const { form, errors, enhance } = superForm(data.form, {
    validators: schema
  });
</script>

<form method="POST" use:enhance class="space-y-6">
  <FormField name="email" {form}>
    <FormLabel>Email</FormLabel>
    <FormDescription>We'll never share your email</FormDescription>
    <Input type="email" bind:value={$form.email} />
    <FormFieldErrors />
  </FormField>

  <FormField name="name" {form}>
    <FormLabel>Full Name</FormLabel>
    <Input bind:value={$form.name} />
    <FormFieldErrors />
  </FormField>

  <FormField name="bio" {form}>
    <FormLabel>Bio</FormLabel>
    <Textarea bind:value={$form.bio} rows={4} />
    <FormFieldErrors />
  </FormField>

  <Button type="submit">Submit</Button>
</form>
```

### Dialog

**File Location:** `/Users/dawiddutoit/projects/play/svelte/src/lib/components/ui/dialog/`

**Usage:**
```svelte
<script lang="ts">
  import {
    Dialog,
    DialogTrigger,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter
  } from '$lib/components/ui/dialog';
  import { Button } from '$lib/components/ui/button';

  let open = $state(false);
</script>

<Dialog bind:open>
  <DialogTrigger asChild>
    <Button variant="outline">Edit Profile</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Edit profile</DialogTitle>
      <DialogDescription>
        Make changes to your profile here. Click save when you're done.
      </DialogDescription>
    </DialogHeader>
    <!-- Form content -->
    <DialogFooter>
      <Button type="submit">Save changes</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

### Tooltip

**File Location:** `/Users/dawiddutoit/projects/play/svelte/src/lib/components/ui/tooltip/`

**Usage:**
```svelte
<script lang="ts">
  import {
    Tooltip,
    TooltipTrigger,
    TooltipContent,
    TooltipProvider
  } from '$lib/components/ui/tooltip';
  import { Button } from '$lib/components/ui/button';
</script>

<TooltipProvider>
  <Tooltip>
    <TooltipTrigger asChild>
      <Button variant="outline">Hover me</Button>
    </TooltipTrigger>
    <TooltipContent>
      <p>Add to library</p>
    </TooltipContent>
  </Tooltip>
</TooltipProvider>
```

### Dropdown Menu

**File Location:** `/Users/dawiddutoit/projects/play/svelte/src/lib/components/ui/dropdown-menu/`

**Usage:**
```svelte
<script lang="ts">
  import {
    DropdownMenu,
    DropdownMenuTrigger,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuCheckboxItem,
    DropdownMenuRadioGroup,
    DropdownMenuRadioItem
  } from '$lib/components/ui/dropdown-menu';
  import { Button } from '$lib/components/ui/button';

  let showStatus = $state(true);
  let position = $state('bottom');
</script>

<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <Button variant="outline">Open Menu</Button>
  </DropdownMenuTrigger>
  <DropdownMenuContent>
    <DropdownMenuLabel>My Account</DropdownMenuLabel>
    <DropdownMenuSeparator />
    <DropdownMenuItem>Profile</DropdownMenuItem>
    <DropdownMenuItem>Settings</DropdownMenuItem>
    <DropdownMenuSeparator />
    <DropdownMenuCheckboxItem bind:checked={showStatus}>
      Show Status
    </DropdownMenuCheckboxItem>
    <DropdownMenuSeparator />
    <DropdownMenuRadioGroup bind:value={position}>
      <DropdownMenuRadioItem value="top">Top</DropdownMenuRadioItem>
      <DropdownMenuRadioItem value="bottom">Bottom</DropdownMenuRadioItem>
    </DropdownMenuRadioGroup>
  </DropdownMenuContent>
</DropdownMenu>
```

---

## Navigation

### Tabs

**File Location:** `/Users/dawiddutoit/projects/play/svelte/src/lib/components/ui/tabs/`

**Usage:**
```svelte
<script lang="ts">
  import {
    Tabs,
    TabsList,
    TabsTrigger,
    TabsContent
  } from '$lib/components/ui/tabs';

  let activeTab = $state('account');
</script>

<Tabs bind:value={activeTab}>
  <TabsList>
    <TabsTrigger value="account">Account</TabsTrigger>
    <TabsTrigger value="password">Password</TabsTrigger>
    <TabsTrigger value="settings">Settings</TabsTrigger>
  </TabsList>
  <TabsContent value="account">
    <p>Make changes to your account here.</p>
  </TabsContent>
  <TabsContent value="password">
    <p>Change your password here.</p>
  </TabsContent>
  <TabsContent value="settings">
    <p>Manage your settings here.</p>
  </TabsContent>
</Tabs>
```

### Breadcrumb

**File Location:** `/Users/dawiddutoit/projects/play/svelte/src/lib/components/ui/breadcrumb/`

**Usage:**
```svelte
<script lang="ts">
  import {
    Breadcrumb,
    BreadcrumbList,
    BreadcrumbItem,
    BreadcrumbLink,
    BreadcrumbPage,
    BreadcrumbSeparator,
    BreadcrumbEllipsis
  } from '$lib/components/ui/breadcrumb';
</script>

<Breadcrumb>
  <BreadcrumbList>
    <BreadcrumbItem>
      <BreadcrumbLink href="/">Home</BreadcrumbLink>
    </BreadcrumbItem>
    <BreadcrumbSeparator />
    <BreadcrumbItem>
      <BreadcrumbLink href="/showcase">Showcase</BreadcrumbLink>
    </BreadcrumbItem>
    <BreadcrumbSeparator />
    <BreadcrumbItem>
      <BreadcrumbPage>Primitives</BreadcrumbPage>
    </BreadcrumbItem>
  </BreadcrumbList>
</Breadcrumb>
```

### Pagination

**File Location:** `/Users/dawiddutoit/projects/play/svelte/src/lib/components/ui/pagination/`

**Usage:**
```svelte
<script lang="ts">
  import {
    Pagination,
    PaginationContent,
    PaginationItem,
    PaginationLink,
    PaginationPrevious,
    PaginationNext,
    PaginationEllipsis
  } from '$lib/components/ui/pagination';

  let currentPage = $state(1);
  const totalPages = 10;
</script>

<Pagination>
  <PaginationContent>
    <PaginationItem>
      <PaginationPrevious href="?page={currentPage - 1}" />
    </PaginationItem>
    {#each Array(totalPages) as _, i}
      <PaginationItem>
        <PaginationLink href="?page={i + 1}" isActive={currentPage === i + 1}>
          {i + 1}
        </PaginationLink>
      </PaginationItem>
    {/each}
    <PaginationItem>
      <PaginationNext href="?page={currentPage + 1}" />
    </PaginationItem>
  </PaginationContent>
</Pagination>
```

---

## Data Display

### Accordion

**File Location:** `/Users/dawiddutoit/projects/play/svelte/src/lib/components/ui/accordion/`

**Usage:**
```svelte
<script lang="ts">
  import {
    Accordion,
    AccordionItem,
    AccordionTrigger,
    AccordionContent
  } from '$lib/components/ui/accordion';
</script>

<Accordion type="single" collapsible>
  <AccordionItem value="item-1">
    <AccordionTrigger>Is it accessible?</AccordionTrigger>
    <AccordionContent>
      Yes. It adheres to the WAI-ARIA design pattern.
    </AccordionContent>
  </AccordionItem>
  <AccordionItem value="item-2">
    <AccordionTrigger>Is it styled?</AccordionTrigger>
    <AccordionContent>
      Yes. It comes with default styles that you can customize.
    </AccordionContent>
  </AccordionItem>
</Accordion>

<!-- Multiple items open -->
<Accordion type="multiple">
  <!-- Items here -->
</Accordion>
```

### Avatar

**File Location:** `/Users/dawiddutoit/projects/play/svelte/src/lib/components/ui/avatar/`

**Usage:**
```svelte
<script lang="ts">
  import { Avatar, AvatarImage, AvatarFallback } from '$lib/components/ui/avatar';
</script>

<Avatar>
  <AvatarImage src="https://github.com/shadcn.png" alt="@shadcn" />
  <AvatarFallback>CN</AvatarFallback>
</Avatar>

<!-- Fallback shown if image fails -->
<Avatar>
  <AvatarImage src="/broken-url.jpg" alt="User" />
  <AvatarFallback>JD</AvatarFallback>
</Avatar>
```

### Table

**File Location:** `/Users/dawiddutoit/projects/play/svelte/src/lib/components/ui/table/`

**Usage:**
```svelte
<script lang="ts">
  import {
    Table,
    TableHeader,
    TableBody,
    TableFooter,
    TableHead,
    TableRow,
    TableCell,
    TableCaption
  } from '$lib/components/ui/table';

  const invoices = [
    { id: 'INV001', status: 'Paid', amount: '$250.00' },
    { id: 'INV002', status: 'Pending', amount: '$150.00' }
  ];
</script>

<Table>
  <TableCaption>A list of your recent invoices</TableCaption>
  <TableHeader>
    <TableRow>
      <TableHead>Invoice</TableHead>
      <TableHead>Status</TableHead>
      <TableHead class="text-right">Amount</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    {#each invoices as invoice}
      <TableRow>
        <TableCell class="font-medium">{invoice.id}</TableCell>
        <TableCell>{invoice.status}</TableCell>
        <TableCell class="text-right">{invoice.amount}</TableCell>
      </TableRow>
    {/each}
  </TableBody>
  <TableFooter>
    <TableRow>
      <TableCell colspan={2}>Total</TableCell>
      <TableCell class="text-right">$400.00</TableCell>
    </TableRow>
  </TableFooter>
</Table>
```

### Carousel

**File Location:** `/Users/dawiddutoit/projects/play/svelte/src/lib/components/ui/carousel/`

**Usage:**
```svelte
<script lang="ts">
  import {
    Carousel,
    CarouselContent,
    CarouselItem,
    CarouselPrevious,
    CarouselNext
  } from '$lib/components/ui/carousel';
  import { Card, CardContent } from '$lib/components/ui/card';
</script>

<Carousel>
  <CarouselContent>
    {#each Array(5) as _, index}
      <CarouselItem>
        <Card>
          <CardContent class="flex aspect-square items-center justify-center p-6">
            <span class="text-4xl font-semibold">{index + 1}</span>
          </CardContent>
        </Card>
      </CarouselItem>
    {/each}
  </CarouselContent>
  <CarouselPrevious />
  <CarouselNext />
</Carousel>
```

---

## Overlays

### Popover

**File Location:** `/Users/dawiddutoit/projects/play/svelte/src/lib/components/ui/popover/`

**Usage:**
```svelte
<script lang="ts">
  import {
    Popover,
    PopoverTrigger,
    PopoverContent
  } from '$lib/components/ui/popover';
  import { Button } from '$lib/components/ui/button';
</script>

<Popover>
  <PopoverTrigger asChild>
    <Button variant="outline">Open popover</Button>
  </PopoverTrigger>
  <PopoverContent>
    <div class="space-y-2">
      <h4 class="font-medium">Dimensions</h4>
      <p class="text-sm text-muted-foreground">
        Set the dimensions for the layer.
      </p>
    </div>
  </PopoverContent>
</Popover>
```

### Sheet

**File Location:** `/Users/dawiddutoit/projects/play/svelte/src/lib/components/ui/sheet/`

**Usage:**
```svelte
<script lang="ts">
  import {
    Sheet,
    SheetTrigger,
    SheetContent,
    SheetHeader,
    SheetTitle,
    SheetDescription
  } from '$lib/components/ui/sheet';
  import { Button } from '$lib/components/ui/button';
</script>

<Sheet>
  <SheetTrigger asChild>
    <Button variant="outline">Open</Button>
  </SheetTrigger>
  <SheetContent side="right">
    <SheetHeader>
      <SheetTitle>Edit profile</SheetTitle>
      <SheetDescription>
        Make changes to your profile here. Click save when you're done.
      </SheetDescription>
    </SheetHeader>
    <!-- Content here -->
  </SheetContent>
</Sheet>
```

### Drawer

**File Location:** `/Users/dawiddutoit/projects/play/svelte/src/lib/components/ui/drawer/`

**Usage:**
```svelte
<script lang="ts">
  import {
    Drawer,
    DrawerTrigger,
    DrawerContent,
    DrawerHeader,
    DrawerTitle,
    DrawerDescription,
    DrawerFooter,
    DrawerClose
  } from '$lib/components/ui/drawer';
  import { Button } from '$lib/components/ui/button';

  let open = $state(false);
</script>

<Drawer bind:open>
  <DrawerTrigger asChild>
    <Button variant="outline">Open Drawer</Button>
  </DrawerTrigger>
  <DrawerContent>
    <DrawerHeader>
      <DrawerTitle>Are you absolutely sure?</DrawerTitle>
      <DrawerDescription>This action cannot be undone.</DrawerDescription>
    </DrawerHeader>
    <DrawerFooter>
      <Button>Submit</Button>
      <DrawerClose asChild>
        <Button variant="outline">Cancel</Button>
      </DrawerClose>
    </DrawerFooter>
  </DrawerContent>
</Drawer>
```

---

## Feedback

### Progress

**File Location:** `/Users/dawiddutoit/projects/play/svelte/src/lib/components/ui/progress/`

**Usage:**
```svelte
<script lang="ts">
  import { Progress } from '$lib/components/ui/progress';

  let progress = $state(33);

  // Simulate progress
  $effect(() => {
    const timer = setTimeout(() => progress = 66, 500);
    return () => clearTimeout(timer);
  });
</script>

<Progress value={progress} />
```

### Sonner (Toast)

**File Location:** `/Users/dawiddutoit/projects/play/svelte/src/lib/components/ui/sonner/`

**Usage:**
```svelte
<script lang="ts">
  import { toast } from 'svelte-sonner';
  import { Button } from '$lib/components/ui/button';
  import { Toaster } from '$lib/components/ui/sonner';
</script>

<!-- Add to layout -->
<Toaster />

<!-- Trigger toasts -->
<Button onclick={() => toast.success('Event created')}>
  Show Success Toast
</Button>

<Button onclick={() => toast.error('Failed to save')}>
  Show Error Toast
</Button>

<Button onclick={() => toast('Event has been created', {
  description: 'Monday, January 3rd at 6:00pm',
  action: {
    label: 'Undo',
    onClick: () => console.log('Undo')
  }
})}>
  Show Toast with Action
</Button>
```

---

## Custom Components

### ServiceCard

**File Location:** `/Users/dawiddutoit/projects/play/svelte/src/lib/components/ServiceCard.svelte`

**Usage:**
```svelte
<script lang="ts">
  import ServiceCard from '$lib/components/ServiceCard.svelte';
</script>

<ServiceCard
  name="PostgreSQL Database"
  status="online"
  description="Primary application database running PostgreSQL 14"
  publicUrl="https://db.example.com"
  credentials={[
    { label: 'Username', value: 'postgres' },
    { label: 'Password', value: 'secret123' }
  ]}
/>
```

**Props:**
- `name`: `string` - Service name
- `status`: `'online'` | `'offline'` | `'warning'` - Service status
- `description`: `string` - Service description
- `publicUrl`: `string` (optional) - Public URL
- `credentials`: `Array<{label: string, value: string}>` (optional) - Credentials to display

**Features:**
- Expandable card with click-to-copy credentials
- Status indicator with color coding
- Toast notifications on copy
- Svelte transitions for smooth expand/collapse
