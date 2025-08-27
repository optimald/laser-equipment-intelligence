import React, { useState, useEffect } from 'react';

interface Testimonial {
  id: number;
  quote: string;
  name: string;
  title: string;
  company?: string;
  image?: string;
}

const Testimonials: React.FC = () => {
  const [currentTestimonial, setCurrentTestimonial] = useState(0);

  const testimonials: Testimonial[] = [
    {
      id: 1,
      quote: "Sold my laser in 48 hours! LaserMatch.io is a game-changer for anyone looking to buy or sell aesthetic equipment quickly and safely.",
      name: "Dr. Jane Smith",
      title: "Clinic Owner",
      company: "Advanced Aesthetics Center",
      image: "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?ixlib=rb-4.0.3&auto=format&fit=crop&w=150&q=80"
    },
    {
      id: 2,
      quote: "Found the perfect device at half the cost. The platform made it easy to connect with verified sellers and negotiate a fair deal.",
      name: "Dr. John Doe",
      title: "Medical Director",
      company: "Elite Medical Spa",
      image: "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?ixlib=rb-4.0.3&auto=format&fit=crop&w=150&q=80"
    },
    {
      id: 3,
      quote: "The platform is so easy to use. Listings are a breeze and the customer support team is incredibly helpful throughout the entire process.",
      name: "Sarah Lee",
      title: "Equipment Distributor",
      company: "MedTech Solutions",
      image: "https://images.unsplash.com/photo-1594824694996-f2bfce5b9eef?ixlib=rb-4.0.3&auto=format&fit=crop&w=150&q=80"
    },
    {
      id: 4,
      quote: "As a buyer, I saved over $50,000 on my clinic's laser equipment. The quality and verification process gave me complete confidence.",
      name: "Dr. Michael Chen",
      title: "Medical Director",
      company: "Beauty & Wellness Clinic",
      image: "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?ixlib=rb-4.0.3&auto=format&fit=crop&w=150&q=80"
    }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTestimonial((prev) => (prev + 1) % testimonials.length);
    }, 6000);

    return () => clearInterval(interval);
  }, [testimonials.length]);

  return (
    <section id="testimonials" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-secondary mb-6">
            What Our Users Say
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Don't just take our word for it. Hear from medical professionals who have successfully bought and sold equipment through LaserMatch.io
          </p>
        </div>

        {/* Desktop View - 3 Column Grid */}
        <div className="hidden md:grid md:grid-cols-3 gap-8">
          {testimonials.map((testimonial, index) => (
            <div
              key={testimonial.id}
              className="bg-light rounded-xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
              style={{
                animationDelay: `${index * 0.2}s`,
              }}
            >
              {/* Quote */}
              <div className="mb-6">
                <svg className="w-8 h-8 text-primary mb-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L10 4.414 7.707 6.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                </svg>
                <p className="text-gray-700 text-lg italic leading-relaxed">
                  "{testimonial.quote}"
                </p>
              </div>

              {/* Author */}
              <div className="flex items-center">
                {testimonial.image && (
                  <img
                    src={testimonial.image}
                    alt={testimonial.name}
                    className="w-12 h-12 rounded-full object-cover mr-4"
                  />
                )}
                <div>
                  <h4 className="font-bold text-primary text-lg">{testimonial.name}</h4>
                  <p className="text-gray-600">{testimonial.title}</p>
                  {testimonial.company && (
                    <p className="text-gray-500 text-sm">{testimonial.company}</p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Mobile View - Slider */}
        <div className="md:hidden">
          <div className="relative overflow-hidden">
            <div 
              className="flex transition-transform duration-500 ease-in-out"
              style={{ transform: `translateX(-${currentTestimonial * 100}%)` }}
            >
              {testimonials.map((testimonial) => (
                <div key={testimonial.id} className="w-full flex-shrink-0">
                  <div className="bg-light rounded-xl p-8 shadow-lg">
                    {/* Quote */}
                    <div className="mb-6">
                      <svg className="w-8 h-8 text-primary mb-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L10 4.414 7.707 6.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                      </svg>
                      <p className="text-gray-700 text-lg italic leading-relaxed">
                        "{testimonial.quote}"
                      </p>
                    </div>

                    {/* Author */}
                    <div className="flex items-center">
                      {testimonial.image && (
                        <img
                          src={testimonial.image}
                          alt={testimonial.name}
                          className="w-12 h-12 rounded-full object-cover mr-4"
                        />
                      )}
                      <div>
                        <h4 className="font-bold text-primary text-lg">{testimonial.name}</h4>
                        <p className="text-gray-600">{testimonial.title}</p>
                        {testimonial.company && (
                          <p className="text-gray-500 text-sm">{testimonial.company}</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Mobile Dots Indicator */}
            <div className="flex justify-center mt-8 space-x-2">
              {testimonials.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentTestimonial(index)}
                  className={`w-3 h-3 rounded-full transition-all duration-300 ${
                    index === currentTestimonial ? 'bg-primary scale-125' : 'bg-gray-300 hover:bg-gray-400'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center mt-16">
          <p className="text-xl text-gray-600 mb-6">
            Ready to join thousands of satisfied users?
          </p>
          <button className="bg-primary hover:bg-blue-600 text-white font-semibold py-4 px-8 rounded-lg text-lg transition-all duration-300 transform hover:scale-105">
            Start Your Journey
          </button>
          <div className="mt-4">
            <a href="#" className="text-primary hover:text-blue-600 font-medium transition-colors duration-300">
              Read More Success Stories →
            </a>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Testimonials;
