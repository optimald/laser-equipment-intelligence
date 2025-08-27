import React, { useState, useEffect } from 'react';
import InventoryFilters from './InventoryFilters';

interface InventoryItem {
  id: number;
  image: string;
  name: string;
  description: string;
  year?: string;
  price?: string;
  condition: string;
  location: string;
  sellerVerified: boolean;
  warranty: string;
  shipping: string;
}

const InventoryHighlights: React.FC = () => {
  const [currentSlide, setCurrentSlide] = useState(0);

  const inventoryItems: InventoryItem[] = [
    {
      id: 1,
      image: "https://images.unsplash.com/photo-1576091160399-112ba8d25d1f?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80",
      name: "Aerolase LightPod Neo Elite",
      description: "Advanced laser system for hair removal and skin treatments",
      year: "2022+",
      price: "Contact for Price",
      condition: "Excellent",
      location: "New York, NY",
      sellerVerified: true,
      warranty: "6 months remaining",
      shipping: "Free shipping"
    },
    {
      id: 2,
      image: "https://images.unsplash.com/photo-1559757175-0eb30cd8c063?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80",
      name: "Candela GentleMax Pro",
      description: "Dual-wavelength laser for comprehensive treatments",
      year: "2021",
      price: "Contact for Price",
      condition: "Very Good",
      location: "Los Angeles, CA",
      sellerVerified: true,
      warranty: "3 months remaining",
      shipping: "Local pickup available"
    },
    {
      id: 3,
      image: "https://images.unsplash.com/photo-1576091160550-2173dba999ef?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80",
      name: "Cutera Excel V+",
      description: "Vascular and pigment laser treatment system",
      year: "2023",
      price: "Contact for Price",
      condition: "Like New",
      location: "Miami, FL",
      sellerVerified: true,
      warranty: "12 months remaining",
      shipping: "Free shipping"
    },
    {
      id: 4,
      image: "https://images.unsplash.com/photo-1559757175-0eb30cd8c063?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80",
      name: "Lumenis M22",
      description: "Multi-application platform for various skin treatments",
      year: "2022",
      price: "Contact for Price",
      condition: "Excellent",
      location: "Chicago, IL",
      sellerVerified: true,
      warranty: "6 months remaining",
      shipping: "Local pickup available"
    },
    {
      id: 5,
      image: "https://images.unsplash.com/photo-1576091160399-112ba8d25d1f?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80",
      name: "Cynosure PicoSure",
      description: "Picosecond laser for tattoo removal and skin revitalization",
      year: "2021",
      price: "Contact for Price",
      condition: "Good",
      location: "Dallas, TX",
      sellerVerified: true,
      warranty: "Expired",
      shipping: "Free shipping"
    },
    {
      id: 6,
      image: "https://images.unsplash.com/photo-1576091160550-2173dba999ef?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80",
      name: "Sciton HALO",
      description: "Hybrid fractional laser for skin resurfacing",
      year: "2023",
      price: "Contact for Price",
      condition: "Like New",
      location: "Seattle, WA",
      sellerVerified: true,
      warranty: "12 months remaining",
      shipping: "Free shipping"
    }
  ];

  const itemsPerView = {
    mobile: 1,
    tablet: 2,
    desktop: 4
  };

  const totalSlides = Math.ceil(inventoryItems.length / itemsPerView.desktop);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % totalSlides);
    }, 5000);

    return () => clearInterval(interval);
  }, [totalSlides]);

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % totalSlides);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + totalSlides) % totalSlides);
  };

  return (
    <section id="inventory" className="py-20 bg-light">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-secondary mb-6">
            Featured Equipment
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Discover high-quality pre-owned aesthetic equipment from trusted sellers
          </p>
        </div>

        {/* Filters */}
        <InventoryFilters />

        {/* Carousel Container */}
        <div className="relative">
          {/* Carousel */}
          <div className="overflow-hidden">
            <div 
              className="flex transition-transform duration-500 ease-in-out"
              style={{ transform: `translateX(-${currentSlide * 100}%)` }}
            >
              {Array.from({ length: totalSlides }).map((_, slideIndex) => (
                <div key={slideIndex} className="w-full flex-shrink-0">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {inventoryItems
                      .slice(slideIndex * itemsPerView.desktop, (slideIndex + 1) * itemsPerView.desktop)
                      .map((item, index) => (
                        <div
                          key={item.id}
                          className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 overflow-hidden"
                          style={{
                            animationDelay: `${index * 0.1}s`,
                          }}
                        >
                          {/* Image */}
                          <div className="relative overflow-hidden">
                            <img
                              src={item.image}
                              alt={item.name}
                              className="w-full h-48 object-cover transition-transform duration-300 hover:scale-110"
                            />
                            {item.year && (
                              <div className="absolute top-4 right-4 bg-primary text-white px-2 py-1 rounded-full text-sm font-semibold">
                                {item.year}
                              </div>
                            )}
                          </div>

                          {/* Content */}
                          <div className="p-6">
                            <div className="flex items-start justify-between mb-3">
                              <h3 className="text-lg font-bold text-secondary line-clamp-2 flex-1">
                                {item.name}
                              </h3>
                              {item.sellerVerified && (
                                <div className="ml-2 bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full font-medium">
                                  ✓ Verified
                                </div>
                              )}
                            </div>
                            
                            <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                              {item.description}
                            </p>
                            
                            {/* Equipment Details */}
                            <div className="grid grid-cols-2 gap-2 mb-4 text-xs">
                              <div className="flex items-center">
                                <span className="text-gray-500">Condition:</span>
                                <span className="ml-1 font-medium">{item.condition}</span>
                              </div>
                              <div className="flex items-center">
                                <span className="text-gray-500">Location:</span>
                                <span className="ml-1 font-medium">{item.location}</span>
                              </div>
                              <div className="flex items-center">
                                <span className="text-gray-500">Warranty:</span>
                                <span className="ml-1 font-medium">{item.warranty}</span>
                              </div>
                              <div className="flex items-center">
                                <span className="text-gray-500">Shipping:</span>
                                <span className="ml-1 font-medium">{item.shipping}</span>
                              </div>
                            </div>
                            
                            {item.price && (
                              <p className="text-primary font-semibold mb-4 text-center text-lg">
                                {item.price}
                              </p>
                            )}

                            <div className="flex gap-2">
                              <button className="flex-1 bg-primary hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded-lg transition-all duration-300 transform hover:scale-105">
                                Get Quote
                              </button>
                              <button className="bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium py-2 px-3 rounded-lg transition-all duration-300">
                                Quick View
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Navigation Arrows */}
          <button
            onClick={prevSlide}
            className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-4 bg-white hover:bg-gray-50 text-secondary p-3 rounded-full shadow-lg transition-all duration-300 hover:scale-110"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>

          <button
            onClick={nextSlide}
            className="absolute right-0 top-1/2 transform -translate-y-1/2 translate-x-4 bg-white hover:bg-gray-50 text-secondary p-3 rounded-full shadow-lg transition-all duration-300 hover:scale-110"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>

          {/* Dots Indicator */}
          <div className="flex justify-center mt-8 space-x-2">
            {Array.from({ length: totalSlides }).map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentSlide(index)}
                className={`w-3 h-3 rounded-full transition-all duration-300 ${
                  index === currentSlide ? 'bg-primary scale-125' : 'bg-gray-300 hover:bg-gray-400'
                }`}
              />
            ))}
          </div>
        </div>

        {/* View All Button */}
        <div className="text-center mt-12">
          <button className="bg-secondary hover:bg-gray-700 text-white font-semibold py-4 px-8 rounded-lg text-lg transition-all duration-300 transform hover:scale-105">
            View All Equipment
          </button>
        </div>
      </div>
    </section>
  );
};

export default InventoryHighlights;
