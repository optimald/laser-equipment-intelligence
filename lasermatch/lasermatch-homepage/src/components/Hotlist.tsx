import React, { useState } from 'react';

interface HotlistItem {
  id: string;
  title: string;
  description: string;
  category: string;
  location: string;
  urgency?: 'high' | 'medium' | 'low';
  datePosted: string;
}

const Hotlist: React.FC = () => {
  const [email, setEmail] = useState('');
  const [isSubscribed, setIsSubscribed] = useState(false);


  // Sample hotlist data - Only equipment needed (available equipment is shown in main marketplace)
  const hotlistItems: HotlistItem[] = [
    {
      id: '1',
      title: 'CO2 Fractional Laser System',
      description: 'Looking for a reliable CO2 fractional laser for skin resurfacing treatments. Must be in excellent condition with recent service history.',
      category: 'CO2 Lasers',
      location: 'Dallas, TX',
      urgency: 'high',
      datePosted: '2 days ago'
    },
    {
      id: '2',
      title: 'IPL Hair Removal Device',
      description: 'Need IPL system for hair removal treatments. Prefer newer model with multiple handpieces.',
      category: 'IPL Systems',
      location: 'Miami, FL',
      urgency: 'medium',
      datePosted: '1 week ago'
    },
    {
      id: '3',
      title: 'RF Skin Tightening Machine',
      description: 'Seeking RF device for non-surgical skin tightening. Must be FDA approved and include training.',
      category: 'RF Devices',
      location: 'Los Angeles, CA',
      urgency: 'high',
      datePosted: '3 days ago'
    },
    {
      id: '4',
      title: 'Ultrasound Skin Tightening Device',
      description: 'Looking for high-intensity focused ultrasound device for non-invasive skin tightening treatments.',
      category: 'Ultrasound',
      location: 'Houston, TX',
      urgency: 'medium',
      datePosted: '4 days ago'
    },
    {
      id: '5',
      title: 'LED Therapy Panel',
      description: 'Need LED therapy panel for acne treatment and skin rejuvenation. Prefer full-face coverage.',
      category: 'LED Therapy',
      location: 'Seattle, WA',
      urgency: 'low',
      datePosted: '1 week ago'
    }
  ];

  const handleSubscribe = (e: React.FormEvent) => {
    e.preventDefault();
    if (email) {
      // Here you would typically send to your newsletter service
      setIsSubscribed(true);
      setEmail('');
    }
  };

  const getUrgencyColor = (urgency?: 'high' | 'medium' | 'low') => {
    switch (urgency) {
      case 'high': return 'bg-red-500 text-white';
      case 'medium': return 'bg-orange-500 text-white';
      case 'low': return 'bg-yellow-500 text-white';
      default: return 'bg-gray-500 text-white';
    }
  };

  const getUrgencyText = (urgency?: 'high' | 'medium' | 'low') => {
    switch (urgency) {
      case 'high': return 'URGENT';
      case 'medium': return 'MEDIUM';
      case 'low': return 'LOW';
      default: return 'N/A';
    }
  };

  const filteredItems = hotlistItems; // All items are now "needed" type

  return (
    <section id="hotlist" className="py-16 lg:py-24 bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="relative">
              <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-red-600 rounded-full flex items-center justify-center hotlist-glow">
                <svg className="w-8 h-8 text-white hotlist-flicker" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="absolute -top-1 -right-1 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center animate-pulse">
                <span className="text-xs font-bold text-white">HOT</span>
              </div>
            </div>
            <h2 className="text-4xl sm:text-5xl font-bold text-white">
              LaserMatch <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-red-500">Hotlist</span>
            </h2>
          </div>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Stay ahead of the market with real-time updates on equipment needed and available. 
            Get instant notifications when your perfect match appears.
          </p>
        </div>

        {/* Newsletter Subscription */}
        <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 mb-12 border border-white/20">
          <div className="text-center">
            <h3 className="text-2xl font-bold text-white mb-4">
              🔥 Get the Hotlist First!
            </h3>
            <p className="text-gray-300 mb-6">
              Subscribe to receive weekly updates on equipment needs and availability. 
              Never miss a perfect match again.
            </p>
            
            {!isSubscribed ? (
              <form onSubmit={handleSubscribe} className="max-w-md mx-auto">
                <div className="flex gap-3">
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your email address"
                    className="flex-1 px-4 py-3 rounded-lg border-0 focus:outline-none focus:ring-2 focus:ring-orange-500 text-gray-900"
                    required
                  />
                  <button
                    type="submit"
                    className="px-6 py-3 bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 text-white font-semibold rounded-lg transition-all duration-300 transform hover:scale-105"
                  >
                    Subscribe
                  </button>
                </div>
                <p className="text-xs text-gray-400 mt-2">
                  We respect your privacy. Unsubscribe at any time.
                </p>
              </form>
            ) : (
              <div className="bg-green-500/20 border border-green-500/30 rounded-lg p-4">
                <p className="text-green-400 font-medium">
                  🎉 You're subscribed to the Hotlist! Check your email for confirmation.
                </p>
              </div>
            )}
          </div>
        </div>

                {/* Section Title */}
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-white mb-2">🔥 Equipment Needed</h2>
          <p className="text-gray-300 text-lg">Clinics looking for specific equipment</p>
        </div>

        {/* Hotlist Items */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredItems.map((item) => (
            <div
              key={item.id}
              className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 hover:border-orange-500/50 transition-all duration-300 hover:transform hover:scale-105 hover:shadow-lg hover:shadow-red-500/20"
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-1 rounded-full text-xs font-bold bg-red-500 text-white">
                    🔥 NEEDED
                  </span>
                  {item.urgency && (
                    <span className={`px-2 py-1 rounded-full text-xs font-bold ${getUrgencyColor(item.urgency)}`}>
                      {getUrgencyText(item.urgency)}
                    </span>
                  )}
                </div>
                <span className="text-xs text-gray-400">{item.datePosted}</span>
              </div>

              {/* Content */}
              <h3 className="text-lg font-bold text-white mb-2">{item.title}</h3>
              <p className="text-gray-300 text-sm mb-4 line-clamp-3">{item.description}</p>
              
              {/* Details */}
              <div className="space-y-2 mb-4">
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-gray-400">Category:</span>
                  <span className="text-white font-medium">{item.category}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-gray-400">Region:</span>
                  <span className="text-white font-medium">{item.location.split(',')[1]?.trim() || 'Multiple Locations'}</span>
                </div>
              </div>

              {/* Brokered Contact */}
              <div className="pt-4 border-t border-white/20">
                <div className="text-center mb-3">
                  <span className="text-xs text-gray-400">All sales are brokered through LaserMatch</span>
                </div>
                <button className="w-full px-4 py-2 bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 text-white text-sm font-medium rounded-lg transition-all duration-300">
                  Contact Broker
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Call to Action */}
        <div className="text-center mt-12">
          <p className="text-gray-300 mb-6">
            Need equipment that's not listed? Post your requirements!
          </p>
          <div className="flex justify-center">
            <button className="px-8 py-4 bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 text-white font-semibold rounded-lg transition-all duration-300 transform hover:scale-105">
              🔥 Post Equipment Needed
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hotlist;
