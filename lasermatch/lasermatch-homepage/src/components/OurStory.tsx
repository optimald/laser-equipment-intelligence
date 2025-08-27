import React from 'react';

const OurStory: React.FC = () => {
  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Story Content */}
          <div className="animate-slide-in-left">
            <h2 className="text-3xl sm:text-4xl font-bold text-secondary mb-6">
              Our Story
            </h2>
            <div className="space-y-4 mb-6">
              <p className="text-lg text-gray-600 leading-relaxed">
                LaserMatch.io was born from a real problem we experienced firsthand. As medical professionals, we saw how the high cost of aesthetic equipment was preventing clinics from offering cutting-edge treatments to their patients.
              </p>
              
              <h4 className="text-xl font-semibold text-secondary mt-6 mb-3">The Problem We Solved</h4>
              <ul className="list-disc list-inside space-y-2 text-gray-600 ml-4">
                <li>Equipment costs 60-80% higher than necessary</li>
                <li>No trusted marketplace for pre-owned devices</li>
                <li>Lack of verification and quality assurance</li>
                <li>Slow, fragmented buying and selling process</li>
              </ul>
              
              <p className="text-lg text-gray-600 leading-relaxed mt-6">
                We discovered that many clinics had perfectly good equipment sitting unused, while others desperately needed affordable options to expand their services. The traditional marketplace was fragmented, slow, and lacked trust.
              </p>
              
              <h4 className="text-xl font-semibold text-secondary mt-6 mb-3">Our Solution</h4>
              <p className="text-lg text-gray-600 leading-relaxed">
                That's why we built LaserMatch.io – a trusted platform where medical professionals can buy and sell pre-owned aesthetic equipment with confidence. We're not just a marketplace; we're a community dedicated to making advanced treatments accessible to everyone.
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <svg className="w-6 h-6 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span className="text-gray-600 font-medium">Founded by Medical Professionals</span>
              </div>
            </div>
          </div>

          {/* Visual Element */}
          <div className="relative">
            <div className="bg-gradient-to-br from-primary/10 to-blue-300/20 rounded-2xl p-8 lg:p-12">
              <div className="text-center">
                <div className="text-6xl mb-4" role="img" aria-label="Medical clinic building">🏥</div>
                <h3 className="text-2xl font-bold text-secondary mb-4">
                  Trusted by 500+ Clinics
                </h3>
                <p className="text-gray-600">
                  Join the community that's transforming how medical equipment changes hands
                </p>
              </div>
            </div>
            
            {/* Floating Stats */}
            <div className="absolute -top-4 -right-4 bg-white rounded-lg shadow-lg p-4 border border-gray-100">
              <div className="text-2xl font-bold text-primary">48hrs</div>
              <div className="text-sm text-gray-600">Avg. Sale Time</div>
            </div>
            
            <div className="absolute -bottom-4 -left-4 bg-white rounded-lg shadow-lg p-4 border border-gray-100">
              <div className="text-2xl font-bold text-primary">$2M+</div>
              <div className="text-sm text-gray-600">Equipment Sold</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default OurStory;
