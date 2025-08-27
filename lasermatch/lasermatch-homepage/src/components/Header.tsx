import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import logoImage from '../assets/logo.png';

const Header: React.FC = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const isHomePage = location.pathname === '/';

  return (
    <>
      {/* Mobile App Promotion Banner */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-2 px-4 text-center text-sm">
        <div className="max-w-7xl mx-auto flex items-center justify-center gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
          <span>📱 Download our mobile app for the best experience!</span>
          <a href="#mobile-app" className="underline hover:no-underline font-medium">
            Learn More
          </a>
        </div>
      </div>
      
      <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled ? 'bg-white shadow-lg' : 'bg-transparent'
      } ${isScrolled ? 'sticky' : ''}`} style={{ top: isScrolled ? '0' : '40px' }}>
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16 lg:h-20">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/">
              <img
                src={logoImage}
                alt="LaserMatch"
                className={`h-8 w-auto sm:h-10 transition-all duration-300 ${
                  isScrolled ? 'filter brightness-0' : 'filter invert brightness-0'
                }`}
              />
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-10">
            {isHomePage ? (
              <>
                <a
                  href="#hotlist"
                  className={`font-medium transition-colors duration-300 hover:scale-105 ${
                    isScrolled 
                      ? 'text-secondary hover:text-primary' 
                      : 'text-white hover:text-blue-300'
                  }`}
                  onClick={(e) => {
                    e.preventDefault();
                    document.getElementById('hotlist')?.scrollIntoView({ behavior: 'smooth' });
                  }}
                >
                  Equipment Needed
                </a>
                <a
                  href="#marketplace"
                  className={`font-medium transition-colors duration-300 hover:scale-105 ${
                    isScrolled 
                      ? 'text-secondary hover:text-primary' 
                      : 'text-white hover:text-blue-300'
                  }`}
                  onClick={(e) => {
                    e.preventDefault();
                    document.getElementById('marketplace')?.scrollIntoView({ behavior: 'smooth' });
                  }}
                >
                  Browse Equipment
                </a>
                <a
                  href="#mobile-app"
                  className={`font-medium transition-colors duration-300 hover:scale-105 ${
                    isScrolled 
                      ? 'text-secondary hover:text-primary' 
                      : 'text-white hover:text-blue-300'
                  }`}
                  onClick={(e) => {
                    e.preventDefault();
                    document.getElementById('mobile-app')?.scrollIntoView({ behavior: 'smooth' });
                  }}
                >
                  Mobile App
                </a>
                <a
                  href="#testimonials"
                  className={`font-medium transition-colors duration-300 hover:scale-105 ${
                    isScrolled 
                      ? 'text-secondary hover:text-primary' 
                      : 'text-white hover:text-blue-300'
                  }`}
                  onClick={(e) => {
                    e.preventDefault();
                    document.getElementById('testimonials')?.scrollIntoView({ behavior: 'smooth' });
                  }}
                >
                  Testimonials
                </a>
              </>
            ) : (
              <Link
                to="/"
                className={`font-medium transition-colors duration-300 hover:scale-105 ${
                  isScrolled 
                    ? 'text-secondary hover:text-primary' 
                    : 'text-gray-700 hover:text-blue-600'
                }`}
              >
                Home
              </Link>
            )}
            
            <Link
              to="/concept"
              className={`font-medium transition-colors duration-300 hover:scale-105 ${
                isScrolled 
                  ? 'text-secondary hover:text-primary' 
                  : isHomePage ? 'text-white hover:text-blue-300' : 'text-gray-700 hover:text-blue-600'
              }`}
            >
              Concept
            </Link>
            
            <button className="bg-white hover:bg-gray-100 text-primary font-semibold py-3 px-8 rounded-lg transition-all duration-300 transform hover:scale-105 border-2 border-white">
              Sign In
            </button>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className={`p-2 rounded-md ${
                isScrolled ? 'text-secondary' : isHomePage ? 'text-white' : 'text-gray-700'
              }`}
            >
              <svg
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                {isMobileMenuOpen ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-gray-200">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {isHomePage ? (
                <>
                  <a
                    href="#hotlist"
                    className="block px-3 py-2 text-secondary hover:text-primary font-medium transition-colors duration-300"
                    onClick={() => {
                      setIsMobileMenuOpen(false);
                      document.getElementById('hotlist')?.scrollIntoView({ behavior: 'smooth' });
                    }}
                  >
                    Equipment Needed
                  </a>
                  <a
                    href="#marketplace"
                    className="block px-3 py-2 text-secondary hover:text-primary font-medium transition-colors duration-300"
                    onClick={() => {
                      setIsMobileMenuOpen(false);
                      document.getElementById('marketplace')?.scrollIntoView({ behavior: 'smooth' });
                    }}
                  >
                    Browse Equipment
                  </a>
                  <a
                    href="#mobile-app"
                    className="block px-3 py-2 text-secondary hover:text-primary font-medium transition-colors duration-300"
                    onClick={() => {
                      setIsMobileMenuOpen(false);
                      document.getElementById('mobile-app')?.scrollIntoView({ behavior: 'smooth' });
                    }}
                  >
                    Mobile App
                  </a>
                  <a
                    href="#testimonials"
                    className="block px-3 py-2 text-secondary hover:text-primary font-medium transition-colors duration-300"
                    onClick={() => {
                      setIsMobileMenuOpen(false);
                      document.getElementById('testimonials')?.scrollIntoView({ behavior: 'smooth' });
                    }}
                  >
                    Testimonials
                  </a>
                </>
              ) : (
                <Link
                  to="/"
                  className="block px-3 py-2 text-secondary hover:text-primary font-medium transition-colors duration-300"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Home
                </Link>
              )}
              
              <Link
                to="/concept"
                className="block px-3 py-2 text-secondary hover:text-primary font-medium transition-colors duration-300"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                Concept
              </Link>
              
              <button className="w-full mt-2 bg-primary hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded-lg transition-all duration-300">
                Sign In
              </button>
            </div>
          </div>
        )}
      </nav>
    </header>
    </>
  );
};

export default Header;
