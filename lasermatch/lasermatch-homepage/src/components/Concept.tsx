import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ChevronLeft, 
  ChevronRight, 
  Users, 
  Shield, 
  Zap, 
  ArrowLeft,
  Package,
  BarChart3,
  Download,
  CreditCard,
  Database,
  Lightbulb,
  Target,
  ClipboardList,
  Bell,
  Settings,
  Rocket,
  TrendingUp
} from 'lucide-react';

interface Slide {
  id: number;
  title: string;
  subtitle: string;
  description: string;
  features: string[];
  icon: React.ReactNode;
  color: string;
  image?: string;
}

const slides: Slide[] = [
  {
    id: 1,
    title: "LaserMatch 3.0",
    subtitle: "Unified Marketplace + Procurement Platform",
    description: "A comprehensive solution replacing manual spreadsheets and fragmented communication with a live, structured system for aesthetic/medical device trading.",
    features: [
      "Simplify Inventory Input",
      "Match Supply & Demand",
      "Replace Manual Spreadsheets",
      "Create Market Liquidity"
    ],
    icon: <Lightbulb className="w-16 h-16 text-yellow-500" />,
    color: "from-blue-600 to-purple-600"
  },
  {
    id: 2,
    title: "Core Objectives",
    subtitle: "Strategic Platform Goals",
    description: "LaserMatch 3.0 addresses the fundamental challenges in medical device procurement and trading, creating a unified ecosystem for all stakeholders.",
    features: [
      "Simplify Inventory Input for Reps & Clinics",
      "Centralize Buyer Want-Lists & Auto-Matching",
      "Migrate from Manual Spreadsheets",
      "Ensure Trust & Transaction Transparency"
    ],
    icon: <Target className="w-16 h-16 text-blue-500" />,
    color: "from-blue-500 to-cyan-500"
  },
  {
    id: 3,
    title: "User Roles & Permissions",
    subtitle: "Multi-Stakeholder Platform Access",
    description: "Comprehensive role-based access control designed for internal buyers, external sellers, and administrators with specific permissions and capabilities.",
    features: [
      "Internal Buyers (Procurement Team)",
      "External Sellers (Clinics, Reps, Brokers)",
      "Administrators (MRP / LaserMatch Team)",
      "Role-Based Access Control"
    ],
    icon: <Users className="w-16 h-16 text-green-500" />,
    color: "from-green-500 to-emerald-500"
  },
  {
    id: 4,
    title: "Inventory Input System",
    subtitle: "Mobile-First Equipment Upload",
    description: "Streamlined equipment listing with smart form autofill, photo/video uploads, and comprehensive condition assessment for accurate market representation.",
    features: [
      "Mobile-First Photo/Video Upload (60 sec max)",
      "Smart Form Autofill (Brand/Model Database)",
      "Condition + Pricing Assessment",
      "Verification Step with Serial Numbers"
    ],
    icon: <Package className="w-16 h-16 text-red-500" />,
    color: "from-red-500 to-pink-500"
  },
  {
    id: 5,
    title: "Buyer Want-List Management",
    subtitle: "Centralized Procurement Planning",
    description: "Spreadsheet-like interface for procurement teams to maintain device requirements, track status, and receive automatic match notifications.",
    features: [
      "Spreadsheet-Like Grid Interface",
      "CSV Bulk Upload for Legacy Data",
      "Status Tracking (Open, Pending, Closed)",
      "Budget & Urgency Management"
    ],
    icon: <ClipboardList className="w-16 h-16 text-indigo-500" />,
    color: "from-indigo-500 to-purple-500"
  },
  {
    id: 6,
    title: "AI-Powered Matching Engine",
    subtitle: "Real-Time Supply & Demand Matching",
    description: "Advanced matching algorithm that automatically connects buyers with available inventory based on device specifications, condition, and pricing.",
    features: [
      "Real-Time Auto-Matching Algorithm",
      "Ranking by Match Percentage",
      "Geographic & Price Optimization",
      "Matching Dashboard with Filters"
    ],
    icon: <Zap className="w-16 h-16 text-teal-500" />,
    color: "from-teal-500 to-blue-500"
  },
  {
    id: 7,
    title: "Notifications & Communication",
    subtitle: "Multi-Channel Alert System",
    description: "Comprehensive notification system ensuring all parties stay informed about matches, updates, and critical procurement opportunities.",
    features: [
      "Push Notifications (Mobile App)",
      "Email + SMS Alert System",
      "WhatsApp Bot Integration",
      "Configurable Notification Preferences"
    ],
    icon: <Bell className="w-16 h-16 text-purple-500" />,
    color: "from-purple-500 to-pink-500"
  },
  {
    id: 8,
    title: "Transaction Workflow",
    subtitle: "Secure & Streamlined Trading",
    description: "End-to-end transaction management including escrow payments, shipping integration, and trade credit systems for enhanced market liquidity.",
    features: [
      "Escrow Payment Protection",
      "Pre-Negotiated Shipping Integration",
      "Trade Credit System",
      "Complete Transaction Tracking"
    ],
    icon: <CreditCard className="w-16 h-16 text-orange-500" />,
    color: "from-orange-500 to-red-500"
  },
  {
    id: 9,
    title: "Trust & Reputation System",
    subtitle: "Verified & Reliable Trading",
    description: "Comprehensive trust mechanisms including seller verification, rating systems, and fraud prevention to ensure secure and reliable transactions.",
    features: [
      "Verified Seller Badge System",
      "5-Star Rating & Review System",
      "Fraud Prevention & Detection",
      "Serial Number Validation"
    ],
    icon: <Shield className="w-16 h-16 text-cyan-500" />,
    color: "from-cyan-500 to-blue-500"
  },
  {
    id: 10,
    title: "Administrative Tools",
    subtitle: "Comprehensive Platform Management",
    description: "Full administrative control with audit logging, listing approval queues, and analytics dashboards for platform oversight and optimization.",
    features: [
      "Complete Audit Logging",
      "Listing Approval Queue Management",
      "Analytics Dashboard & Reporting",
      "User Access & Permission Control"
    ],
    icon: <Settings className="w-16 h-16 text-green-500" />,
    color: "from-green-500 to-teal-500"
  },
  {
    id: 11,
    title: "Platform Architecture",
    subtitle: "Modern Tech Stack & Infrastructure",
    description: "Scalable architecture built with modern technologies including mobile apps, web dashboards, and cloud-based backend services.",
    features: [
      "Mobile App (React Native / Expo)",
      "Web App (Next.js) for Buyers & Admin",
      "Backend (Node.js + Supabase/Postgres)",
      "Cloud Storage (AWS S3 / Supabase)"
    ],
    icon: <Database className="w-16 h-16 text-blue-500" />,
    color: "from-blue-500 to-indigo-500"
  },
  {
    id: 12,
    title: "Core Platform Features",
    subtitle: "Essential Platform Capabilities",
    description: "Essential features for platform launch including mobile app for sellers, buyer dashboard, basic matching, and admin verification tools.",
    features: [
      "Mobile App for Sellers",
      "Buyer Dashboard + Want-Lists",
      "Basic Matching Engine",
      "Admin Panel + CSV Import"
    ],
    icon: <Rocket className="w-16 h-16 text-red-500" />,
    color: "from-red-500 to-orange-500"
  },
  {
    id: 13,
    title: "Advanced Features & Integration",
    subtitle: "Enhanced Platform Capabilities",
    description: "Enhanced platform capabilities including escrow payments, logistics integration, advanced notifications, and reputation systems.",
    features: [
      "Escrow Payments + Trade Credits",
      "Logistics Integration & Quotes",
      "Advanced Notifications (WhatsApp/SMS)",
      "Reputation & Badge System"
    ],
    icon: <TrendingUp className="w-16 h-16 text-purple-500" />,
    color: "from-purple-500 to-pink-500"
  },
  {
    id: 14,
    title: "Enterprise & Advanced Analytics",
    subtitle: "Professional & Enterprise Features",
    description: "Long-term platform evolution including API access, advanced analytics, white-label options, and additional financial services.",
    features: [
      "API Access for Enterprise Systems",
      "Advanced Analytics & Forecasting",
      "White-Label Distribution Options",
      "Financing & Insurance Services"
    ],
    icon: <BarChart3 className="w-16 h-16 text-emerald-500" />,
    color: "from-emerald-500 to-green-500"
  },
  {
    id: 15,
    title: "Success Metrics & Monetization",
    subtitle: "Business Model & KPIs",
    description: "Comprehensive success tracking and revenue generation through listing fees, transaction fees, subscriptions, and value-added services.",
    features: [
      "Active Listings & Match Rates",
      "Transaction Volume & User Retention",
      "Listing Fees + Transaction Fees (3-5%)",
      "Subscription Plans & Add-On Services"
    ],
    icon: <Lightbulb className="w-16 h-16 text-purple-500" />,
    color: "from-purple-600 to-pink-600"
  }
];

const Concept: React.FC = () => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isExporting, setIsExporting] = useState(false);

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % slides.length);
  };

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + slides.length) % slides.length);
  };

  const goToSlide = (index: number) => {
    setCurrentSlide(index);
  };

  const exportToPDF = async () => {
    setIsExporting(true);
    
    try {
      // Dynamic import of jsPDF
      const jsPDF = (await import('jspdf')).default;
      
      // Use portrait orientation for better compatibility
      const pdf = new jsPDF('p', 'mm', 'a4');
      
      // Get page dimensions
      const pageHeight = pdf.internal.pageSize.getHeight(); // 297mm for portrait A4
      
      // Set PDF metadata
      pdf.setProperties({
        title: 'LaserMatch 3.0 Platform Concept',
        subject: 'Medical Equipment Marketplace Platform Overview',
        author: 'LaserMatch.io Team',
        creator: 'LaserMatch 3.0 Platform'
      });

      // Add title page
      pdf.setFontSize(24);
      pdf.setTextColor(59, 130, 246); // Blue color
      pdf.text('LaserMatch 3.0 Platform Concept', 105, 40, { align: 'center' });
      
      pdf.setFontSize(16);
      pdf.setTextColor(107, 114, 128); // Gray color
      pdf.text('Medical Equipment Marketplace Platform Overview', 105, 55, { align: 'center' });
      
      pdf.setFontSize(12);
      pdf.setTextColor(156, 163, 175);
      pdf.text(`Generated on ${new Date().toLocaleDateString()}`, 105, 70, { align: 'center' });
      
      pdf.setFontSize(14);
      pdf.setTextColor(75, 85, 99);
      pdf.text('Table of Contents:', 20, 90);
      
      // Add table of contents with proper spacing
      slides.forEach((slide, index) => {
        const yPos = 105 + (index * 7); // Reduced spacing to fit more items
        if (yPos < 280) { // Check if we have space on this page
          pdf.setFontSize(11);
          pdf.setTextColor(59, 130, 246);
          pdf.text(`${index + 1}.`, 20, yPos);
          pdf.setTextColor(75, 85, 99);
          // Truncate long titles to fit on one line
          const title = slide.title.length > 50 ? slide.title.substring(0, 47) + '...' : slide.title;
          pdf.text(title, 30, yPos);
        }
      });

      // Add each slide as a new page
      for (let i = 0; i < slides.length; i++) {
        // Add new page for each slide
        pdf.addPage();
        
        const slide = slides[i];
        
        // Slide title
        pdf.setFontSize(20);
        pdf.setTextColor(59, 130, 246);
        pdf.text(slide.title, 20, 30);
        
        // Slide subtitle
        pdf.setFontSize(16);
        pdf.setTextColor(107, 114, 128);
        pdf.text(slide.subtitle, 20, 45);
        
        // Slide description
        pdf.setFontSize(12);
        pdf.setTextColor(75, 85, 99);
        const descriptionLines = pdf.splitTextToSize(slide.description, 170);
        pdf.text(descriptionLines, 20, 65);
        
        // Slide features
        pdf.setFontSize(14);
        pdf.setTextColor(59, 130, 246);
        pdf.text('Key Features:', 20, 120);
        
        slide.features.forEach((feature, index) => {
          const yPos = 135 + (index * 8);
          pdf.setFontSize(11);
          pdf.setTextColor(75, 85, 99);
          pdf.text(`• ${feature}`, 25, yPos);
        });
        
        // Slide number and page number
        pdf.setFontSize(12);
        pdf.setTextColor(59, 130, 246);
        pdf.text(`Slide ${i + 1} of ${slides.length}`, 20, pageHeight - 20);
        pdf.setTextColor(156, 163, 175);
        pdf.text(`Page ${i + 2} of ${slides.length + 1}`, 105, pageHeight - 20, { align: 'center' });
      }

      // Save the PDF
      pdf.save('LaserMatch-3.0-Platform-Concept.pdf');
      
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Error generating PDF. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Minimal Header */}
      <header className="bg-white/90 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-3">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <Link
                to="/"
                className="inline-flex items-center gap-2 text-gray-600 hover:text-blue-600 transition-colors duration-200 text-sm"
              >
                <ArrowLeft className="w-4 h-4" />
                Back to Home
              </Link>
              <span className="text-gray-400">|</span>
              <h1 className="text-lg font-semibold text-gray-900">Platform Concept</h1>
            </div>
            
            <button
              onClick={exportToPDF}
              disabled={isExporting}
              className="flex items-center space-x-2 px-3 py-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 disabled:opacity-50 text-white rounded-lg transition-all font-medium text-sm"
            >
              <Download className="w-4 h-4" />
              <span>{isExporting ? 'Generating...' : 'Export PDF'}</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center p-4 pt-6">
        <div className="max-w-6xl w-full">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentSlide}
              initial={{ opacity: 0, x: 100 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -100 }}
              transition={{ duration: 0.5 }}
              className="bg-white rounded-3xl shadow-2xl overflow-hidden"
              id="slide-content"
            >
              {/* Slide Content */}
              <div className="p-8 md:p-12">
                <div className="text-center mb-8">
                  <div className="flex justify-center mb-4">
                    {slides[currentSlide].icon}
                  </div>
                  <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
                    {slides[currentSlide].title}
                  </h1>
                  <p className="text-xl text-gray-600 mb-4">
                    {slides[currentSlide].subtitle}
                  </p>
                  <p className="text-lg text-gray-700 max-w-3xl mx-auto">
                    {slides[currentSlide].description}
                  </p>
                </div>

                {/* Features Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                  {slides[currentSlide].features.map((feature, index) => (
                    <div
                      key={index}
                      className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg"
                    >
                      <div className="w-2 h-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"></div>
                      <span className="text-gray-700">{feature}</span>
                    </div>
                  ))}
                </div>

                {/* Slide Navigation */}
                <div className="flex justify-center space-x-2 mb-8">
                  {slides.map((_, index) => (
                    <button
                      key={index}
                      onClick={() => goToSlide(index)}
                      className={`w-3 h-3 rounded-full transition-colors ${
                        index === currentSlide
                          ? 'bg-gradient-to-r from-blue-500 to-purple-500'
                          : 'bg-gray-500 hover:bg-gray-400'
                      }`}
                    />
                  ))}
                </div>

                {/* Navigation Buttons */}
                <div className="flex justify-between items-center">
                  <button
                    onClick={prevSlide}
                    className="flex items-center space-x-2 px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
                  >
                    <ChevronLeft className="w-5 h-5" />
                    <span>Previous</span>
                  </button>

                  <div className="text-sm text-gray-500">
                    {currentSlide + 1} of {slides.length}
                  </div>

                  <button
                    onClick={nextSlide}
                    className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg transition-colors"
                  >
                    <span>Next</span>
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </motion.div>
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
};

export default Concept;
