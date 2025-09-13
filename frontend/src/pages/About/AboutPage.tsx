// src/pages/About/AboutPage.tsx
import React from 'react';
import { Card, Row, Col, Timeline, Statistic } from 'antd';
import { 
  CheckCircleOutlined, 
  TrophyOutlined, 
  TeamOutlined, 
  GlobalOutlined,
  PrinterOutlined,
  BgColorsOutlined,
  CustomerServiceOutlined,
  ThunderboltOutlined
} from '@ant-design/icons';

const AboutPage: React.FC = () => {
  const stats = [
    { title: 'Happy Customers', value: 5000, suffix: '+', icon: <TeamOutlined /> },
    { title: 'Projects Completed', value: 15000, suffix: '+', icon: <PrinterOutlined /> },
    { title: 'Years of Experience', value: 8, suffix: '+', icon: <TrophyOutlined /> },
    { title: 'Design Templates', value: 500, suffix: '+', icon: <BgColorsOutlined /> }
  ];

  const values = [
    {
      icon: <CheckCircleOutlined className="text-4xl text-blue-500" />,
      title: 'Quality First',
      description: 'We never compromise on quality. Every print goes through rigorous quality checks to ensure perfection.'
    },
    {
      icon: <ThunderboltOutlined className="text-4xl text-yellow-500" />,
      title: 'Fast Delivery',
      description: 'Time is money. We ensure quick turnaround times without compromising on quality or attention to detail.'
    },
    {
      icon: <CustomerServiceOutlined className="text-4xl text-green-500" />,
      title: 'Customer Support',
      description: '24/7 customer support to help you with your printing needs. We\'re here whenever you need us.'
    },
    {
      icon: <BgColorsOutlined className="text-4xl text-purple-500" />,
      title: 'Design Innovation',
      description: 'Cutting-edge design tools and templates to help you create stunning prints that stand out.'
    }
  ];

  const timeline = [
    {
      color: 'blue',
      children: (
        <div>
          <h4 className="font-semibold">2016 - The Beginning</h4>
          <p className="text-gray-600">Started as a small printing shop with a vision to provide quality printing services.</p>
        </div>
      )
    },
    {
      color: 'green',
      children: (
        <div>
          <h4 className="font-semibold">2018 - Digital Transformation</h4>
          <p className="text-gray-600">Introduced online ordering system and expanded our digital printing capabilities.</p>
        </div>
      )
    },
    {
      color: 'orange',
      children: (
        <div>
          <h4 className="font-semibold">2020 - Design Tool Launch</h4>
          <p className="text-gray-600">Launched our revolutionary online design tool, making design accessible to everyone.</p>
        </div>
      )
    },
    {
      color: 'purple',
      children: (
        <div>
          <h4 className="font-semibold">2022 - Expansion</h4>
          <p className="text-gray-600">Expanded operations across multiple cities and introduced eco-friendly printing options.</p>
        </div>
      )
    },
    {
      color: 'red',
      children: (
        <div>
          <h4 className="font-semibold">2024 - Innovation Continues</h4>
          <p className="text-gray-600">Launched AI-powered design suggestions and enhanced our online platform.</p>
        </div>
      )
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-50 to-blue-100 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            About <span className="text-primary-600">Drishthi Printing</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            We're passionate about bringing your ideas to life through high-quality printing solutions. 
            Since 2016, we've been helping businesses and individuals create stunning prints that make an impact.
          </p>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Row gutter={32}>
            {stats.map((stat, index) => (
              <Col xs={12} sm={6} key={index}>
                <Card className="text-center h-full">
                  <div className="text-3xl text-primary-500 mb-3">
                    {stat.icon}
                  </div>
                  <Statistic
                    title={stat.title}
                    value={stat.value}
                    suffix={stat.suffix}
                    valueStyle={{ color: '#3981e6', fontSize: '2rem', fontWeight: 'bold' }}
                  />
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      </section>

      {/* Our Story Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Row gutter={48} align="middle">
            <Col xs={24} lg={12}>
              <div>
                <h2 className="text-3xl font-bold text-gray-900 mb-6">Our Story</h2>
                <div className="space-y-4 text-gray-600 leading-relaxed">
                  <p>
                    Drishthi Printing began with a simple belief: everyone deserves access to professional-quality 
                    printing services, regardless of their design experience or budget.
                  </p>
                  <p>
                    What started as a small printing shop has evolved into a comprehensive digital printing platform 
                    that serves thousands of customers across India. We've maintained our commitment to quality while 
                    embracing technology to make printing more accessible than ever.
                  </p>
                  <p>
                    Our revolutionary design tool has democratized the design process, allowing anyone to create 
                    professional-looking materials without needing extensive design knowledge. We're proud to have 
                    helped countless businesses establish their brand identity and individuals bring their creative 
                    visions to life.
                  </p>
                  <p>
                    Today, we continue to innovate and expand our services, always keeping our customers' needs at 
                    the heart of everything we do.
                  </p>
                </div>
              </div>
            </Col>
            <Col xs={24} lg={12}>
              <div className="bg-white p-8 rounded-lg shadow-lg">
                <h3 className="text-xl font-semibold text-gray-900 mb-6">Our Journey</h3>
                <Timeline>
                  {timeline.map((item, index) => (
                    <Timeline.Item key={index} color={item.color}>
                      {item.children}
                    </Timeline.Item>
                  ))}
                </Timeline>
              </div>
            </Col>
          </Row>
        </div>
      </section>

      {/* Our Values Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Our Values</h2>
            <p className="text-lg text-gray-600">
              The principles that guide everything we do
            </p>
          </div>

          <Row gutter={32}>
            {values.map((value, index) => (
              <Col xs={24} sm={12} lg={6} key={index}>
                <Card className="h-full text-center hover:shadow-lg transition-shadow duration-300">
                  <div className="mb-4">
                    {value.icon}
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">
                    {value.title}
                  </h3>
                  <p className="text-gray-600">
                    {value.description}
                  </p>
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      </section>

      {/* Mission & Vision Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Row gutter={48}>
            <Col xs={24} lg={12}>
              <Card className="h-full">
                <div className="text-center mb-6">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <GlobalOutlined className="text-2xl text-blue-600" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900">Our Mission</h3>
                </div>
                <p className="text-gray-600 text-center leading-relaxed">
                  To make professional-quality printing accessible to everyone by combining cutting-edge technology 
                  with exceptional service. We strive to empower our customers with the tools and support they need 
                  to bring their creative visions to life.
                </p>
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card className="h-full">
                <div className="text-center mb-6">
                  <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <TrophyOutlined className="text-2xl text-purple-600" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900">Our Vision</h3>
                </div>
                <p className="text-gray-600 text-center leading-relaxed">
                  To be the leading digital printing platform in India, known for innovation, quality, and customer 
                  satisfaction. We envision a future where anyone can create professional marketing materials and 
                  bring their ideas to life with just a few clicks.
                </p>
              </Card>
            </Col>
          </Row>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Our Team</h2>
            <p className="text-lg text-gray-600">
              The passionate people behind Drishthi Printing
            </p>
          </div>

          <div className="text-center">
            <Card className="max-w-2xl mx-auto">
              <div className="py-8">
                <TeamOutlined className="text-6xl text-primary-500 mb-6" />
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  A Dedicated Team of Professionals
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  Our team consists of experienced designers, printing specialists, customer service representatives, 
                  and technology experts who are all committed to delivering exceptional results. We work together 
                  to ensure every project meets our high standards of quality and customer satisfaction.
                </p>
                <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                  <div>
                    <div className="text-2xl font-bold text-primary-600">25+</div>
                    <div className="text-sm text-gray-600">Team Members</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-primary-600">8+</div>
                    <div className="text-sm text-gray-600">Years Experience</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-primary-600">10+</div>
                    <div className="text-sm text-gray-600">Design Experts</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-primary-600">24/7</div>
                    <div className="text-sm text-gray-600">Support Available</div>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-primary-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Start Your Project?
          </h2>
          <p className="text-primary-100 text-lg mb-8 max-w-2xl mx-auto">
            Join thousands of satisfied customers who trust Drishthi Printing for their printing needs. 
            Let's bring your ideas to life together.
          </p>
          <div className="space-x-4">
            <a
              href="/products"
              className="bg-white text-primary-600 hover:bg-gray-100 font-semibold text-lg px-8 py-3 rounded-lg transition-colors duration-200 inline-block"
            >
              Browse Products
            </a>
            <a
              href="/contact"
              className="bg-transparent border-2 border-white text-white hover:bg-white hover:text-primary-600 font-semibold text-lg px-8 py-3 rounded-lg transition-colors duration-200 inline-block"
            >
              Contact Us
            </a>
          </div>
        </div>
      </section>
    </div>
  );
};

export default AboutPage;