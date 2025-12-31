# BoosterBoxPro Frontend

Modern Next.js frontend for BoosterBoxPro - TCG Booster Box Market Intelligence Platform.

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ installed
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Install additional dependencies (if not already installed)
npm install axios @tanstack/react-query recharts react-hook-form zod @hookform/resolvers
```

### Environment Variables

Create `.env.local` file (already created with defaults):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_ENVIRONMENT=development
```

### Development

```bash
# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## 📁 Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── (auth)/            # Auth routes (login, register)
│   ├── (dashboard)/       # Protected routes (dashboard, boxes, account)
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Landing page
├── components/
│   ├── ui/                # Reusable UI components
│   ├── charts/            # Chart components
│   ├── box/               # Box-specific components
│   └── auth/              # Auth components
├── lib/
│   ├── api/               # API client functions
│   │   ├── client.ts      # Axios instance & interceptors
│   │   ├── auth.ts        # Authentication endpoints
│   │   ├── leaderboard.ts # Leaderboard endpoints
│   │   └── box.ts         # Box detail endpoints
│   └── types.ts           # TypeScript types
├── hooks/                 # React hooks
├── public/
│   └── images/
│       └── logo.png       # App logo (add your logo here)
└── styles/
    └── globals.css        # Global styles + Tailwind + custom colors
```

## 🎨 Design System

- **Colors**: Logo-inspired palette (Rocket Red, Sky Blue, Flame Orange)
- **Theme**: Dark mode only (Night Sky theme)
- **See**: `../Planning Documents/COLOR_PALETTE.md` for complete color system

## 📚 Documentation

- **Frontend Development Plan**: `../Planning Documents/FRONTEND_DEVELOPMENT_PLAN.md`
- **Design Specs**: `../Planning Documents/BOX_DETAIL_PAGE_DESIGN.md`, `LEADERBOARD_TABLE_DESIGN.md`
- **Logo Guidelines**: `../Planning Documents/LOGO_USAGE_GUIDELINES.md`

## 🛠 Tech Stack

- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query (React Query)
- **HTTP Client**: Axios
- **Charts**: Recharts
- **Forms**: React Hook Form + Zod

## 📝 Next Steps

1. Add logo file to `public/images/logo.png`
2. Create authentication pages (login, register)
3. Build navigation component with logo
4. Create leaderboard page
5. Build box detail page
6. Add charts and advanced features

See `../Planning Documents/FRONTEND_READY_CHECKLIST.md` for detailed checklist.
