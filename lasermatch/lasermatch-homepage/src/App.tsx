
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Hero from './components/Hero';
import OurStory from './components/OurStory';
import Features from './components/Features';
import Hotlist from './components/Hotlist';
import MarketplaceLayout from './components/MarketplaceLayout';
import MobileAppPromo from './components/MobileAppPromo';
import Testimonials from './components/Testimonials';
import CTABanner from './components/CTABanner';
import Footer from './components/Footer';
import Concept from './components/Concept';
import { FilterProvider } from './contexts/FilterContext';

function HomePage() {
  return (
    <div className="min-h-screen">
      <Header />
      <main>
        <Hero />
        <OurStory />
        <Features />
        <Hotlist />
        <FilterProvider>
          <MarketplaceLayout />
        </FilterProvider>
        <MobileAppPromo />
        <Testimonials />
        <CTABanner />
      </main>
      <Footer />
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/concept" element={<Concept />} />
      </Routes>
    </Router>
  );
}

export default App;
