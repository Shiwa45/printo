// src/pages/Contact/ContactPage.tsx
import React, { useState } from 'react';
import { Card, Form, Input, Button, Row, Col, message, Select } from 'antd';
import {
  PhoneOutlined,
  MailOutlined,
  EnvironmentOutlined,
  ClockCircleOutlined,
  CustomerServiceOutlined,
  MessageOutlined,
  UserOutlined
} from '@ant-design/icons';

const { TextArea } = Input;
const { Option } = Select;

const ContactPage: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      // TODO: Implement API call to send contact form
      console.log('Contact form submitted:', values);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      message.success('Thank you for your message! We\'ll get back to you within 24 hours.');
      form.resetFields();
    } catch (error) {
      console.error('Failed to send message:', error);
      message.error('Failed to send message. Please try again or contact us directly.');
    } finally {
      setLoading(false);
    }
  };

  const contactInfo = [
    {
      icon: <PhoneOutlined className="text-2xl text-blue-500" />,
      title: 'Phone',
      details: ['+91 98765 43210', '+91 98765 43211'],
      description: 'Call us for immediate assistance'
    },
    {
      icon: <MailOutlined className="text-2xl text-green-500" />,
      title: 'Email',
      details: ['info@drishthiprinting.com', 'support@drishthiprinting.com'],
      description: 'Send us an email anytime'
    },
    {
      icon: <EnvironmentOutlined className="text-2xl text-red-500" />,
      title: 'Address',
      details: ['123 Business District', 'Mumbai, Maharashtra 400001'],
      description: 'Visit our office'
    },
    {
      icon: <ClockCircleOutlined className="text-2xl text-purple-500" />,
      title: 'Business Hours',
      details: ['Mon - Fri: 9:00 AM - 7:00 PM', 'Sat: 10:00 AM - 5:00 PM'],
      description: 'We\'re here to help'
    }
  ];

  const faqItems = [
    {
      question: 'What is the typical turnaround time?',
      answer: 'Most orders are completed within 24-48 hours. Rush delivery is available for urgent orders.'
    },
    {
      question: 'Do you offer design services?',
      answer: 'Yes! We have a powerful online design tool, plus our design team can help create custom designs.'
    },
    {
      question: 'What file formats do you accept?',
      answer: 'We accept PDF, PNG, JPG, SVG, and designs created with our online design tool.'
    },
    {
      question: 'Do you deliver across India?',
      answer: 'Yes, we deliver pan-India. Free shipping is available for orders above ₹1000.'
    },
    {
      question: 'Can I get a quote before ordering?',
      answer: 'Absolutely! Use our online pricing calculator or contact us for a detailed quote.'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-50 to-blue-100 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Get in <span className="text-primary-600">Touch</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Have a question or need assistance? We're here to help! 
            Reach out to us and we'll respond as quickly as possible.
          </p>
        </div>
      </section>

      {/* Contact Info Cards */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Row gutter={[24, 24]}>
            {contactInfo.map((info, index) => (
              <Col xs={24} sm={12} lg={6} key={index}>
                <Card className="text-center h-full hover:shadow-lg transition-shadow duration-300">
                  <div className="mb-4">
                    {info.icon}
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {info.title}
                  </h3>
                  {info.details.map((detail, idx) => (
                    <p key={idx} className="text-gray-600 mb-1">
                      {detail}
                    </p>
                  ))}
                  <p className="text-sm text-gray-500 mt-2">
                    {info.description}
                  </p>
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      </section>

      {/* Contact Form & Map */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Row gutter={[48, 48]}>
            {/* Contact Form */}
            <Col xs={24} lg={12}>
              <Card>
                <div className="mb-6">
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">
                    Send us a Message
                  </h2>
                  <p className="text-gray-600">
                    Fill out the form below and we'll get back to you within 24 hours.
                  </p>
                </div>

                <Form
                  form={form}
                  layout="vertical"
                  onFinish={handleSubmit}
                  size="large"
                >
                  <Row gutter={16}>
                    <Col span={12}>
                      <Form.Item
                        name="first_name"
                        label="First Name"
                        rules={[{ required: true, message: 'Please enter your first name' }]}
                      >
                        <Input prefix={<UserOutlined />} placeholder="Your first name" />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item
                        name="last_name"
                        label="Last Name"
                        rules={[{ required: true, message: 'Please enter your last name' }]}
                      >
                        <Input prefix={<UserOutlined />} placeholder="Your last name" />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Form.Item
                    name="email"
                    label="Email Address"
                    rules={[
                      { required: true, message: 'Please enter your email' },
                      { type: 'email', message: 'Please enter a valid email' }
                    ]}
                  >
                    <Input prefix={<MailOutlined />} placeholder="your@email.com" />
                  </Form.Item>

                  <Form.Item
                    name="phone"
                    label="Phone Number"
                    rules={[{ required: true, message: 'Please enter your phone number' }]}
                  >
                    <Input prefix={<PhoneOutlined />} placeholder="Your phone number" />
                  </Form.Item>

                  <Form.Item
                    name="subject"
                    label="Subject"
                    rules={[{ required: true, message: 'Please select a subject' }]}
                  >
                    <Select placeholder="What can we help you with?">
                      <Option value="general">General Inquiry</Option>
                      <Option value="quote">Request Quote</Option>
                      <Option value="support">Technical Support</Option>
                      <Option value="design">Design Assistance</Option>
                      <Option value="order">Order Status</Option>
                      <Option value="complaint">Complaint</Option>
                      <Option value="feedback">Feedback</Option>
                    </Select>
                  </Form.Item>

                  <Form.Item
                    name="message"
                    label="Message"
                    rules={[
                      { required: true, message: 'Please enter your message' },
                      { min: 10, message: 'Message must be at least 10 characters' }
                    ]}
                  >
                    <TextArea
                      rows={4}
                      placeholder="Tell us more about your inquiry..."
                      maxLength={1000}
                      showCount
                    />
                  </Form.Item>

                  <Form.Item>
                    <Button
                      type="primary"
                      htmlType="submit"
                      loading={loading}
                      block
                      icon={<MessageOutlined />}
                      className="h-12 text-lg font-medium"
                    >
                      Send Message
                    </Button>
                  </Form.Item>
                </Form>
              </Card>
            </Col>

            {/* Map & Additional Info */}
            <Col xs={24} lg={12}>
              <div className="space-y-6">
                {/* Map */}
                <Card>
                  <h3 className="text-xl font-semibold text-gray-900 mb-4">
                    Find Us
                  </h3>
                  <div className="bg-gray-100 h-64 rounded-lg flex items-center justify-center">
                    <div className="text-center text-gray-500">
                      <EnvironmentOutlined style={{ fontSize: 48 }} className="mb-4" />
                      <p>Interactive Map</p>
                      <p className="text-sm">123 Business District, Mumbai</p>
                    </div>
                  </div>
                </Card>

                {/* Quick Support */}
                <Card>
                  <h3 className="text-xl font-semibold text-gray-900 mb-4">
                    Need Immediate Help?
                  </h3>
                  <div className="space-y-4">
                    <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
                      <CustomerServiceOutlined className="text-xl text-blue-500" />
                      <div>
                        <p className="font-medium text-gray-900">Live Chat</p>
                        <p className="text-sm text-gray-600">Available 9 AM - 7 PM</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg">
                      <PhoneOutlined className="text-xl text-green-500" />
                      <div>
                        <p className="font-medium text-gray-900">Call Us</p>
                        <p className="text-sm text-gray-600">+91 98765 43210</p>
                      </div>
                    </div>

                    <div className="flex items-center space-x-3 p-3 bg-purple-50 rounded-lg">
                      <MailOutlined className="text-xl text-purple-500" />
                      <div>
                        <p className="font-medium text-gray-900">Email Support</p>
                        <p className="text-sm text-gray-600">support@drishthiprinting.com</p>
                      </div>
                    </div>
                  </div>
                </Card>
              </div>
            </Col>
          </Row>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-16 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Frequently Asked Questions
            </h2>
            <p className="text-lg text-gray-600">
              Quick answers to common questions
            </p>
          </div>

          <div className="space-y-4">
            {faqItems.map((faq, index) => (
              <Card key={index} className="hover:shadow-md transition-shadow duration-300">
                <h4 className="font-semibold text-gray-900 mb-2">
                  {faq.question}
                </h4>
                <p className="text-gray-600">
                  {faq.answer}
                </p>
              </Card>
            ))}
          </div>

          <div className="text-center mt-8">
            <p className="text-gray-600 mb-4">
              Can't find what you're looking for?
            </p>
            <Button type="primary" size="large">
              View All FAQs
            </Button>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-primary-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-primary-100 text-lg mb-8">
            Explore our products or try our design tool today!
          </p>
          <div className="space-x-4">
            <a
              href="/products"
              className="bg-white text-primary-600 hover:bg-gray-100 font-semibold text-lg px-8 py-3 rounded-lg transition-colors duration-200 inline-block"
            >
              Browse Products
            </a>
            <a
              href="/design/templates"
              className="bg-transparent border-2 border-white text-white hover:bg-white hover:text-primary-600 font-semibold text-lg px-8 py-3 rounded-lg transition-colors duration-200 inline-block"
            >
              Try Design Tool
            </a>
          </div>
        </div>
      </section>
    </div>
  );
};

export default ContactPage;