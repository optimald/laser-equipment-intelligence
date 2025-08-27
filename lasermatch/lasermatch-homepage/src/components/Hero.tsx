import React from 'react';
import heroImage from '../assets/AdobeStock_1291288780_Preview.jpeg';

const Hero: React.FC = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background Image with Overlay */}
      <div className="absolute inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-br from-gray-900/80 via-gray-800/75 to-gray-900/85 z-10"></div>
        <img
          src={heroImage}
          alt="Professional medical laser equipment in clinical setting"
          className="w-full h-full object-cover"
        />
      </div>

      {/* Content */}
      <div className="relative z-20 text-center px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
        <div className="animate-fade-in-up">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white mb-6 leading-tight">
            Connect with Buyers & Sellers of{' '}
            <span className="text-blue-400">Aesthetic Equipment</span>
          </h1>
          
          <p className="text-xl sm:text-2xl text-gray-200 mb-8 max-w-3xl mx-auto">
            LaserMatch.io: Your Trusted Solution for Pre-Owned Aesthetic Devices
          </p>

          {/* Search Bar */}
          <div className="w-full max-w-2xl mx-auto mb-8">
            <div className="relative">
              <input
                type="text"
                placeholder="Search for equipment (e.g., 'laser', 'IPL', 'fractional')"
                className="w-full px-6 py-4 text-lg rounded-lg border-0 shadow-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
              <button className="absolute right-2 top-2 bg-primary hover:bg-blue-600 text-white p-2 rounded-lg transition-all duration-300">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
            </div>
          </div>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button className="bg-primary hover:bg-blue-600 text-white font-semibold py-4 px-8 rounded-lg text-lg transition-all duration-300 transform hover:scale-105 animate-pulse-glow min-w-[200px]">
              List Your Equipment
            </button>
            <button className="border-2 border-white text-white hover:bg-white hover:text-primary font-semibold py-4 px-8 rounded-lg text-lg transition-all duration-300 min-w-[200px]">
              Find Equipment
            </button>
          </div>
        </div>


      </div>
    </section>
  );
};

export default Hero;
