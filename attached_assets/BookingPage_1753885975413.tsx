import { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Calendar } from './ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover';
import { CalendarIcon, CheckCircle, Clock, MapPin, Phone, Mail, User, Zap } from 'lucide-react';
// Using a simple date formatter to avoid external dependencies
const formatDate = (date: Date) => {
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

interface BookingFormData {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  service: string;
  date: Date | undefined;
  time: string;
  message: string;
}

export default function BookingPage() {
  const [formData, setFormData] = useState<BookingFormData>({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    service: '',
    date: undefined,
    time: '',
    message: ''
  });

  const [isSubmitted, setIsSubmitted] = useState(false);

  const services = [
    { value: 'website-design', label: 'Website Design & Development', price: '$2,500 - $5,000' },
    { value: 'website-redesign', label: 'Website Redesign', price: '$1,500 - $3,500' },
    { value: 'seo-audit', label: 'SEO Audit & Optimization', price: '$500 - $1,200' },
    { value: 'maintenance', label: 'Website Maintenance', price: '$200 - $500/month' },
    { value: 'consultation', label: 'Strategy Consultation', price: 'FREE - $300' }
  ];

  const timeSlots = [
    '9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM',
    '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM', '5:00 PM'
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Here you would typically send the data to your backend
    setIsSubmitted(true);
  };

  const handleInputChange = (field: keyof BookingFormData, value: string | Date | undefined) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  if (isSubmitted) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
        <div className="max-w-md w-full text-center space-y-6">
          <div className="w-20 h-20 mx-auto bg-green-500 rounded-full flex items-center justify-center">
            <CheckCircle className="w-10 h-10 text-white" />
          </div>
          <div className="space-y-4">
            <h2 className="text-white text-2xl">Booking Confirmed!</h2>
            <p className="text-gray-300">
              Thank you for your booking request. We'll contact you within 24 hours to confirm your appointment details.
            </p>
            <Button 
              onClick={() => setIsSubmitted(false)}
              className="bg-pink-600 hover:bg-pink-700 text-white"
            >
              Book Another Appointment
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex justify-center gap-3 mb-6">
            <span className="bg-green-500/20 text-green-400 px-3 py-1 rounded-full text-sm border border-green-500/30">
              ⚡ 20+ DFW Startups Launched
            </span>
            <span className="bg-orange-500/20 text-orange-400 px-3 py-1 rounded-full text-sm border border-orange-500/30">
              🕒 2-Week Launch Timeline
            </span>
            <span className="bg-purple-500/20 text-purple-400 px-3 py-1 rounded-full text-sm border border-purple-500/30">
              💰 Starting at $800
            </span>
          </div>
          
          <h1 className="text-4xl md:text-6xl mb-6">
            <span className="text-pink-500">Book Your Free</span>{' '}
            <span className="text-white">Website Consultation</span>
          </h1>
          
          <p className="text-gray-300 text-lg md:text-xl max-w-3xl mx-auto">
            Schedule a <span className="text-pink-500">professional consultation</span> that helps{' '}
            <span className="text-pink-500">DFW Startups & Small Businesses</span> grow online
          </p>
        </div>

        {/* Stats Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="text-center">
            <div className="text-3xl md:text-4xl text-pink-500 mb-2">$3,200</div>
            <div className="text-gray-300 text-sm">Average Revenue Increase</div>
            <div className="text-gray-400 text-xs">First 3 Months</div>
          </div>
          <div className="text-center">
            <div className="text-3xl md:text-4xl text-pink-500 mb-2">75%</div>
            <div className="text-gray-300 text-sm">Client Credibility Boost</div>
            <div className="text-gray-400 text-xs">vs. DIY Websites</div>
          </div>
          <div className="text-center">
            <div className="text-3xl md:text-4xl text-pink-500 mb-2">4x</div>
            <div className="text-gray-300 text-sm">More Leads Generated</div>
            <div className="text-gray-400 text-xs">Than Social Media Only</div>
          </div>
        </div>

        {/* Alert Box */}
        <div className="bg-red-900/30 border border-red-500/50 rounded-lg p-4 mb-8">
          <div className="flex items-start gap-3">
            <div className="text-red-400 mt-1">⚠️</div>
            <div className="text-red-200 text-sm">
              <strong>Don't Wait Another Month:</strong> Every day without a professional website is potential revenue lost to competitors. August 2025 is prime season for local business growth!
            </div>
          </div>
        </div>

        {/* Special Offer Box */}
        <div className="bg-green-900/30 border border-green-500/50 rounded-lg p-6 mb-8">
          <div className="flex items-start gap-3">
            <Zap className="text-green-400 mt-1 w-5 h-5" />
            <div>
              <h3 className="text-green-400 text-lg mb-2">🎉 New Business Special: Free Discovery Call + $100 Off*</h3>
              <p className="text-green-200 text-sm">
                Starting a new local business? Schedule your free consultation this month and save $100 on any package. Let's discuss your vision and create a launch plan that fits your budget.
              </p>
              <p className="text-green-200 text-sm mt-2">
                <strong>Claim Your New Business Discount*</strong>
              </p>
            </div>
          </div>
        </div>

        {/* Booking Form */}
        <div className="bg-slate-800/50 rounded-lg p-8 border border-slate-700">
          <h2 className="text-white text-2xl mb-6 text-center">Schedule Your Free Consultation</h2>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Contact Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="firstName" className="text-gray-200">First Name</Label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    id="firstName"
                    type="text"
                    value={formData.firstName}
                    onChange={(e) => handleInputChange('firstName', e.target.value)}
                    className="pl-10 bg-slate-700 border-slate-600 text-white placeholder:text-gray-400"
                    placeholder="John"
                    required
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="lastName" className="text-gray-200">Last Name</Label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    id="lastName"
                    type="text"
                    value={formData.lastName}
                    onChange={(e) => handleInputChange('lastName', e.target.value)}
                    className="pl-10 bg-slate-700 border-slate-600 text-white placeholder:text-gray-400"
                    placeholder="Doe"
                    required
                  />
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="email" className="text-gray-200">Email Address</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    className="pl-10 bg-slate-700 border-slate-600 text-white placeholder:text-gray-400"
                    placeholder="john@example.com"
                    required
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="phone" className="text-gray-200">Phone Number</Label>
                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    id="phone"
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => handleInputChange('phone', e.target.value)}
                    className="pl-10 bg-slate-700 border-slate-600 text-white placeholder:text-gray-400"
                    placeholder="(214) 555-0123"
                    required
                  />
                </div>
              </div>
            </div>

            {/* Service Selection */}
            <div className="space-y-2">
              <Label className="text-gray-200">Service Interested In</Label>
              <Select value={formData.service} onValueChange={(value) => handleInputChange('service', value)}>
                <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                  <SelectValue placeholder="Select a service..." />
                </SelectTrigger>
                <SelectContent className="bg-slate-700 border-slate-600">
                  {services.map((service) => (
                    <SelectItem key={service.value} value={service.value} className="text-white hover:bg-slate-600">
                      <div className="flex flex-col">
                        <span>{service.label}</span>
                        <span className="text-pink-400 text-xs">{service.price}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Date and Time Selection */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-gray-200">Preferred Date</Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className="w-full justify-start text-left font-normal bg-slate-700 border-slate-600 text-white hover:bg-slate-600"
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {formData.date ? formatDate(formData.date) : "Pick a date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0 bg-slate-700 border-slate-600">
                    <Calendar
                      mode="single"
                      selected={formData.date}
                      onSelect={(date) => handleInputChange('date', date)}
                      initialFocus
                      disabled={(date) => date < new Date() || date.getDay() === 0 || date.getDay() === 6}
                      className="text-white"
                    />
                  </PopoverContent>
                </Popover>
              </div>
              
              <div className="space-y-2">
                <Label className="text-gray-200">Preferred Time</Label>
                <Select value={formData.time} onValueChange={(value) => handleInputChange('time', value)}>
                  <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                    <SelectValue placeholder="Select time..." />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-700 border-slate-600">
                    {timeSlots.map((time) => (
                      <SelectItem key={time} value={time} className="text-white hover:bg-slate-600">
                        <div className="flex items-center gap-2">
                          <Clock className="w-4 h-4" />
                          {time}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Message */}
            <div className="space-y-2">
              <Label htmlFor="message" className="text-gray-200">Tell Us About Your Project (Optional)</Label>
              <Textarea
                id="message"
                value={formData.message}
                onChange={(e) => handleInputChange('message', e.target.value)}
                className="bg-slate-700 border-slate-600 text-white placeholder:text-gray-400 min-h-[100px]"
                placeholder="Describe your business, goals, and any specific requirements..."
              />
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              className="w-full bg-pink-600 hover:bg-pink-700 text-white py-3 text-lg"
              disabled={!formData.firstName || !formData.lastName || !formData.email || !formData.phone || !formData.service}
            >
              Schedule Free Consultation
            </Button>
          </form>

          {/* Additional Info */}
          <div className="mt-8 pt-6 border-t border-slate-600">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center text-sm text-gray-300">
              <div className="flex items-center justify-center gap-2">
                <Clock className="w-4 h-4 text-pink-400" />
                <span>30-minute consultation</span>
              </div>
              <div className="flex items-center justify-center gap-2">
                <MapPin className="w-4 h-4 text-pink-400" />
                <span>Video call or in-person</span>
              </div>
              <div className="flex items-center justify-center gap-2">
                <CheckCircle className="w-4 h-4 text-pink-400" />
                <span>No obligation required</span>
              </div>
            </div>
          </div>
        </div>

        {/* Disclosure Section */}
        <div className="mt-12 pt-8 border-t border-slate-600">
          <div className="max-w-4xl mx-auto px-4">
            <div style={{ fontFamily: 'Times New Roman, serif' }} className="text-sm leading-relaxed">
              <p className="mb-4">
                <span style={{ fontWeight: 'bold', color: '#e0218a' }}>* Discount Eligibility Disclosure</span>
              </p>
              <p className="mb-4" style={{ color: '#FFFFFF' }}>
                To qualify for the New Business Special: Free Discovery Call + $100 Off, clients must provide two forms of verifiable proof that their business is newly established and has not previously had a professional website. Acceptable forms of proof include, but are not limited to:
              </p>
              <ul className="list-disc ml-6 mb-4 space-y-2" style={{ color: '#FFFFFF' }}>
                <li>Business registration documents (e.g., LLC formation papers, DBA registration) dated within the last 12 months.</li>
                <li>Recent utility bills or lease agreements for the business premises (dated within the last 6 months).</li>
                <li>Official bank statements for the new business account (showing account opening within the last 12 months).</li>
                <li>Tax identification number (EIN) confirmation letter issued within the last 12 months.</li>
              </ul>
              <p style={{ color: '#FFFFFF' }}>
                This offer is exclusively for businesses genuinely in their startup phase looking to establish their first official online presence.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}