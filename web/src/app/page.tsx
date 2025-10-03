'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'
import LaserMatch from '../components/LaserMatch';

export default function Home() {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000, // 1 minute
        retry: 3,
      },
    },
  }))

  return (
    <QueryClientProvider client={queryClient}>
      <main>
        <LaserMatch />
      </main>
    </QueryClientProvider>
  );
}