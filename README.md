# Laser Equipment Procurement Intelligence Frontend

A Next.js frontend application for the Laser Equipment Procurement Intelligence platform, providing procurement teams with a comprehensive interface to search, configure, and monitor laser equipment sourcing across multiple data sources.

## Features

- **Equipment Search**: Advanced search interface with filters for brand, model, condition, price, and location
- **Source Configuration**: Manage and configure multiple data sources (LaserMatch.io, DOTmed, BidSpotter, etc.)
- **Dashboard**: Real-time monitoring of listings, margins, and system performance
- **Responsive Design**: Mobile-friendly interface built with Tailwind CSS

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Heroicons
- **Forms**: React Hook Form
- **State Management**: React Query (for API calls)

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd laser-procurement-frontend
```

2. Install dependencies:
```bash
npm install
```

3. Copy environment variables:
```bash
cp .env.example .env.local
```

4. Update environment variables in `.env.local`:
```env
API_BASE_URL=http://localhost:8000
```

5. Start the development server:
```bash
npm run dev
```

6. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
src/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   └── globals.css        # Global styles
├── components/            # React components
│   ├── EquipmentSearch.tsx    # Search interface
│   ├── SearchResults.tsx      # Results display
│   ├── SourceConfiguration.tsx # Source management
│   └── Dashboard.tsx          # Analytics dashboard
└── types/                 # TypeScript type definitions
```

## Components

### EquipmentSearch
Advanced search interface allowing users to:
- Search by equipment name, brand, or model
- Filter by condition, price range, and location
- Select specific data sources
- Configure advanced search parameters

### SearchResults
Displays search results with:
- Grid and list view modes
- Sorting options (relevance, price, score, date)
- Detailed equipment information
- Favorites and sharing functionality

### SourceConfiguration
Manages data source settings:
- Enable/disable sources
- Configure crawl frequency and delays
- Monitor source performance
- View source logs and status

### Dashboard
Provides analytics and monitoring:
- Key performance metrics
- Source performance breakdown
- Price trend analysis
- Recent activity feed

## API Integration

The frontend integrates with the Laser Equipment Intelligence backend API:

```typescript
// Example API calls
const searchEquipment = async (params: SearchParams) => {
  const response = await fetch(`${API_BASE_URL}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  })
  return response.json()
}
```

## Deployment

### Vercel (Recommended)

1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard:
   - `API_BASE_URL`: Your backend API URL
3. Deploy automatically on push to main branch

### Manual Deployment

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `API_BASE_URL` | Backend API base URL | Yes |
| `NEXT_PUBLIC_GA_ID` | Google Analytics ID | No |
| `NEXT_PUBLIC_SENTRY_DSN` | Sentry DSN for error tracking | No |

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a pull request

## License

This project is proprietary software. All rights reserved.

## Support

For support and questions:
- Email: support@company.com
- Documentation: [Backend API Docs](../laser-equipment-intelligence/docs/)
# Test git push deployment
# Test change
# Vercel Build Test - Sat Sep 20 12:17:10 MDT 2025
# Force redeploy Sat Sep 20 12:56:01 MDT 2025
# Force Railway rebuild
