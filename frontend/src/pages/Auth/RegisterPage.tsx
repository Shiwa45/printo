// src/pages/Auth/RegisterPage.tsx
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Form } from 'antd';
import Input from 'antd/lib/input';
import Button from 'antd/lib/button';
import Card from 'antd/lib/card';
import message from 'antd/lib/message';
import Checkbox from 'antd/lib/checkbox';
import { UserOutlined, MailOutlined, LockOutlined, PhoneOutlined, HomeOutlined } from '@ant-design/icons';
import { useAuth } from '../../context/AuthContext';
import { RegisterRequest } from '../../types/api';

const RegisterPage: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      const registerData: RegisterRequest = {
        email: values.email,
        password: values.password,
        password_confirm: values.password_confirm,
        first_name: values.first_name,
        last_name: values.last_name,
        phone: values.phone,
        company_name: values.company_name,
      };

      await register(registerData);
      message.success('Registration successful! Welcome to Drishthi Printing!');
      navigate('/');
    } catch (error: any) {
      console.error('Registration failed:', error);
      if (error.response?.data?.errors) {
        // Handle field-specific errors
        const errors = error.response.data.errors;
        Object.keys(errors).forEach(field => {
          form.setFields([{
            name: field,
            errors: errors[field],
          }]);
        });
      } else {
        message.error(error.response?.data?.message || 'Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-primary-600 hover:text-primary-500">
              Sign in here
            </Link>
          </p>
        </div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <Card className="py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <Form
            form={form}
            name="register"
            onFinish={onFinish}
            layout="vertical"
            size="large"
            requiredMark={false}
          >
            {/* Personal Information */}
            <div className="grid grid-cols-2 gap-4">
              <Form.Item
                name="first_name"
                label="First Name"
                rules={[
                  { required: true, message: 'Please enter your first name' },
                  { min: 2, message: 'First name must be at least 2 characters' }
                ]}
              >
                <Input
                  prefix={<UserOutlined className="text-gray-400" />}
                  placeholder="First name"
                />
              </Form.Item>

              <Form.Item
                name="last_name"
                label="Last Name"
                rules={[
                  { required: true, message: 'Please enter your last name' },
                  { min: 2, message: 'Last name must be at least 2 characters' }
                ]}
              >
                <Input
                  prefix={<UserOutlined className="text-gray-400" />}
                  placeholder="Last name"
                />
              </Form.Item>
            </div>

            {/* Contact Information */}
            <Form.Item
              name="email"
              label="Email Address"
              rules={[
                { required: true, message: 'Please enter your email' },
                { type: 'email', message: 'Please enter a valid email address' }
              ]}
            >
              <Input
                prefix={<MailOutlined className="text-gray-400" />}
                placeholder="your@email.com"
              />
            </Form.Item>

            <Form.Item
              name="phone"
              label="Phone Number"
              rules={[
                { pattern: /^[0-9]{10}$/, message: 'Please enter a valid 10-digit phone number' }
              ]}
            >
              <Input
                prefix={<PhoneOutlined className="text-gray-400" />}
                placeholder="9876543210"
                maxLength={10}
              />
            </Form.Item>

            {/* Business Information */}
            <Form.Item
              name="company_name"
              label="Company Name (Optional)"
            >
              <Input
                prefix={<HomeOutlined className="text-gray-400" />}
                placeholder="Your company name"
              />
            </Form.Item>

            {/* Password */}
            <Form.Item
              name="password"
              label="Password"
              rules={[
                { required: true, message: 'Please enter your password' },
                { min: 8, message: 'Password must be at least 8 characters' },
                {
                  pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
                  message: 'Password must contain uppercase, lowercase, and number'
                }
              ]}
              hasFeedback
            >
              <Input.Password
                prefix={<LockOutlined className="text-gray-400" />}
                placeholder="Create a strong password"
              />
            </Form.Item>

            <Form.Item
              name="password_confirm"
              label="Confirm Password"
              dependencies={['password']}
              rules={[
                { required: true, message: 'Please confirm your password' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('password') === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error('Passwords do not match'));
                  },
                }),
              ]}
              hasFeedback
            >
              <Input.Password
                prefix={<LockOutlined className="text-gray-400" />}
                placeholder="Confirm your password"
              />
            </Form.Item>

            {/* Terms and Conditions */}
            <Form.Item
              name="terms"
              valuePropName="checked"
              rules={[
                { validator: (_, value) => value ? Promise.resolve() : Promise.reject(new Error('Please accept the terms and conditions')) }
              ]}
            >
              <Checkbox>
                I agree to the{' '}
                <Link to="/terms" className="text-primary-600 hover:text-primary-500">
                  Terms of Service
                </Link>{' '}
                and{' '}
                <Link to="/privacy" className="text-primary-600 hover:text-primary-500">
                  Privacy Policy
                </Link>
              </Checkbox>
            </Form.Item>

            {/* Marketing Consent */}
            <Form.Item name="marketing_consent" valuePropName="checked">
              <Checkbox>
                I would like to receive promotional emails about new products and special offers
              </Checkbox>
            </Form.Item>

            {/* Submit Button */}
            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                block
                className="h-12 text-lg font-medium"
              >
                Create Account
              </Button>
            </Form.Item>

            {/* Additional Info */}
            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">
                    By creating an account, you get
                  </span>
                </div>
              </div>

              <div className="mt-6 grid grid-cols-1 gap-3">
                <div className="flex items-center text-sm text-gray-600">
                  <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  Access to our powerful design tool
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  Save and manage your designs
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  Order history and tracking
                </div>
                <div className="flex items-center text-sm text-gray-600">
                  <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  Exclusive offers and discounts
                </div>
              </div>
            </div>
          </Form>
        </Card>
      </div>
    </div>
  );
};

export default RegisterPage;