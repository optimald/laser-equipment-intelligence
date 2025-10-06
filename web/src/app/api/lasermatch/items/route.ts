import { NextRequest, NextResponse } from 'next/server'

// Mock LaserMatch data
const mockLaserMatchItems = [
  {
    id: 1,
    title: "Aerolase: Lightpod Neo Elite",
    brand: "Aerolase",
    model: "Lightpod Neo Elite",
    condition: "Used - Good",
    price: 35000,
    location: "California, USA",
    description: "Professional Aerolase Lightpod Neo Elite laser system in good condition.",
    url: "https://lasermatch.io/listing/aerolase-lightpod-neo-elite",
    source: "LaserMatch.io",
    status: "active"
  },
  {
    id: 2,
    title: "Candela: GentleMax Pro",
    brand: "Candela",
    model: "GentleMax Pro",
    condition: "Used - Excellent",
    price: 45000,
    location: "Texas, USA",
    description: "High-quality Candela GentleMax Pro laser system in excellent condition.",
    url: "https://lasermatch.io/listing/candela-gentlemax-pro",
    source: "LaserMatch.io",
    status: "active"
  },
  {
    id: 3,
    title: "Cynosure: Picosure",
    brand: "Cynosure",
    model: "Picosure",
    condition: "Used - Good",
    price: 55000,
    location: "New York, USA",
    description: "Professional Cynosure Picosure laser system for aesthetic treatments.",
    url: "https://lasermatch.io/listing/cynosure-picosure",
    source: "LaserMatch.io",
    status: "active"
  },
  {
    id: 4,
    title: "Lumenis: M22",
    brand: "Lumenis",
    model: "M22",
    condition: "Used - Fair",
    price: 40000,
    location: "Florida, USA",
    description: "Lumenis M22 multi-application platform laser system.",
    url: "https://lasermatch.io/listing/lumenis-m22",
    source: "LaserMatch.io",
    status: "active"
  },
  {
    id: 5,
    title: "Alma: Harmony XL",
    brand: "Alma",
    model: "Harmony XL",
    condition: "Used - Good",
    price: 38000,
    location: "Illinois, USA",
    description: "Alma Harmony XL laser system for comprehensive aesthetic treatments.",
    url: "https://lasermatch.io/listing/alma-harmony-xl",
    source: "LaserMatch.io",
    status: "active"
  },
  {
    id: 6,
    title: "BTL: Exilis Ultra",
    brand: "BTL",
    model: "Exilis Ultra",
    condition: "Used - Excellent",
    price: 42000,
    location: "Nevada, USA",
    description: "BTL Exilis Ultra for body contouring and skin tightening treatments.",
    url: "https://lasermatch.io/listing/btl-exilis-ultra",
    source: "LaserMatch.io",
    status: "active"
  },
  {
    id: 7,
    title: "Cutera: Excel V",
    brand: "Cutera",
    model: "Excel V",
    condition: "Used - Good",
    price: 48000,
    location: "Washington, USA",
    description: "Cutera Excel V laser system for vascular and pigmented lesions.",
    url: "https://lasermatch.io/listing/cutera-excel-v",
    source: "LaserMatch.io",
    status: "active"
  },
  {
    id: 8,
    title: "Sciton: Profile",
    brand: "Sciton",
    model: "Profile",
    condition: "Used - Excellent",
    price: 65000,
    location: "Oregon, USA",
    description: "Sciton Profile laser platform for comprehensive aesthetic treatments.",
    url: "https://lasermatch.io/listing/sciton-profile",
    source: "LaserMatch.io",
    status: "active"
  }
]

export async function GET(request: NextRequest) {
  try {
    const url = new URL(request.url)
    const limit = url.searchParams.get('limit')
    
    let items = mockLaserMatchItems
    if (limit) {
      const limitNum = parseInt(limit)
      items = items.slice(0, limitNum)
    }
    
    return NextResponse.json({
      items: items,
      total: mockLaserMatchItems.length,
      source: "mock-api"
    })
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to fetch items" },
      { status: 500 }
    )
  }
}
