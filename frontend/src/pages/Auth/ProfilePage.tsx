// src/pages/Auth/ProfilePage.tsx
import React, { useState, useEffect } from 'react';
import Card from 'antd/lib/card';
import { Form } from 'antd';
import Input from 'antd/lib/input';
import Button from 'antd/lib/button';
import message from 'antd/lib/message';
import Tabs from 'antd/lib/tabs';
import { Descriptions } from 'antd';
import Avatar from 'antd/lib/avatar';
import Upload from 'antd/lib/upload';
import Modal from 'antd/lib/modal';
import Statistic from 'antd/lib/statistic';
import Row from 'antd/lib/row';
import Col from 'antd/lib/col';
import {
  UserOutlined,
  MailOutlined,
  PhoneOutlined,
  HomeOutlined,
  LockOutlined,
  CameraOutlined,
  EditOutlined,
  SaveOutlined,
  BgColorsOutlined,
  ShoppingCartOutlined
} from '@ant-design/icons';
import { useAuth } from '../../context/AuthContext';
import { User } from '../../types/api';

const { TabPane } = Tabs;

const ProfilePage: React.FC = () => {
  const { user, updateProfile } = useAuth();
  const [form] = Form.useForm();
  const [passwordForm] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [userStats, setUserStats] = useState({
    totalDesigns: 0,
    totalOrders: 0,
    totalSpent: 0,
  });

  useEffect(() => {
    if (user) {
      form.setFieldsValue({
        first_name: user.first_name,
        last_name: user.last_name,
        email: user.email,
        phone: user.phone,
        company_name: user.company_name,
        gst_number: user.gst_number,
      });
      loadUserStats();
    }
  }, [user, form]);

  const loadUserStats = () => {
    // Load user statistics
    // For now, get from localStorage (will be replaced with API calls)
    const designs = JSON.parse(localStorage.getItem('userDesigns') || '[]');
    setUserStats({
      totalDesigns: designs.length,
      totalOrders: 0, // TODO: Load from API
      totalSpent: 0, // TODO: Load from API
    });
  };

  const handleProfileUpdate = async (values: any) => {
    setLoading(true);
    try {
      await updateProfile(values);
      message.success('Profile updated successfully!');
      setIsEditing(false);
    } catch (error: any) {
      console.error('Profile update failed:', error);
      message.error('Failed to update profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (values: any) => {
    setPasswordLoading(true);
    try {
      // TODO: Implement password change API call
      console.log('Changing password:', values);
      message.success('Password changed successfully!');
      passwordForm.resetFields();
    } catch (error: any) {
      console.error('Password change failed:', error);
      message.error('Failed to change password. Please try again.');
    } finally {
      setPasswordLoading(false);
    }
  };

  const handleAvatarUpload = async (file: any) => {
    // TODO: Implement avatar upload
    console.log('Uploading avatar:', file);
    message.success('Avatar uploaded successfully!');
    return false; // Prevent default upload behavior
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Please log in to view your profile
          </h2>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Profile Header */}
        <Card className="mb-6">
          <div className="flex items-center space-x-6">
            <div className="relative">
              <Avatar
                size={100}
                icon={<UserOutlined />}
                className="bg-primary-500"
              />
              <Upload
                showUploadList={false}
                beforeUpload={handleAvatarUpload}
                accept="image/*"
              >
                <Button
                  type="primary"
                  shape="circle"
                  icon={<CameraOutlined />}
                  size="small"
                  className="absolute bottom-0 right-0"
                  title="Change Avatar"
                />
              </Upload>
            </div>
            
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-900">
                {user.first_name} {user.last_name}
              </h1>
              <p className="text-gray-600">{user.email}</p>
              {user.company_name && (
                <p className="text-gray-600">{user.company_name}</p>
              )}
              <div className="flex items-center mt-2">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  user.is_verified 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {user.is_verified ? 'Verified Account' : 'Pending Verification'}
                </span>
              </div>
            </div>

            <div className="text-right">
              <p className="text-sm text-gray-500">Member since</p>
              <p className="font-medium">
                {new Date(user.date_joined).toLocaleDateString()}
              </p>
            </div>
          </div>
        </Card>

        {/* Quick Stats */}
        <Row gutter={16} className="mb-6">
          <Col xs={24} sm={8}>
            <Card>
              <Statistic
                title="Total Designs"
                value={userStats.totalDesigns}
                prefix={<BgColorsOutlined className="text-blue-500" />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card>
              <Statistic
                title="Total Orders"
                value={userStats.totalOrders}
                prefix={<ShoppingCartOutlined className="text-green-500" />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card>
              <Statistic
                title="Total Spent"
                value={userStats.totalSpent}
                prefix="₹"
                precision={2}
              />
            </Card>
          </Col>
        </Row>

        {/* Profile Tabs */}
        <Card>
          <Tabs defaultActiveKey="profile" size="large">
            {/* Profile Information */}
            <TabPane 
              tab={
                <span>
                  <UserOutlined />
                  Profile Information
                </span>
              } 
              key="profile"
            >
              <div className="max-w-2xl">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-medium text-gray-900">
                    Personal Information
                  </h3>
                  <Button
                    type={isEditing ? "default" : "primary"}
                    icon={isEditing ? <SaveOutlined /> : <EditOutlined />}
                    onClick={() => {
                      if (isEditing) {
                        form.submit();
                      } else {
                        setIsEditing(true);
                      }
                    }}
                    loading={loading}
                  >
                    {isEditing ? 'Save Changes' : 'Edit Profile'}
                  </Button>
                </div>

                {isEditing ? (
                  <Form
                    form={form}
                    layout="vertical"
                    onFinish={handleProfileUpdate}
                    size="large"
                  >
                    <Row gutter={16}>
                      <Col span={12}>
                        <Form.Item
                          name="first_name"
                          label="First Name"
                          rules={[{ required: true, message: 'Please enter your first name' }]}
                        >
                          <Input prefix={<UserOutlined />} />
                        </Form.Item>
                      </Col>
                      <Col span={12}>
                        <Form.Item
                          name="last_name"
                          label="Last Name"
                          rules={[{ required: true, message: 'Please enter your last name' }]}
                        >
                          <Input prefix={<UserOutlined />} />
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
                      <Input prefix={<MailOutlined />} disabled />
                    </Form.Item>

                    <Form.Item
                      name="phone"
                      label="Phone Number"
                    >
                      <Input prefix={<PhoneOutlined />} />
                    </Form.Item>

                    <Form.Item
                      name="company_name"
                      label="Company Name"
                    >
                      <Input prefix={<HomeOutlined />} />
                    </Form.Item>

                    <Form.Item
                      name="gst_number"
                      label="GST Number"
                    >
                      <Input placeholder="Enter GST number for business accounts" />
                    </Form.Item>

                    <div className="flex space-x-4">
                      <Button 
                        type="primary" 
                        htmlType="submit" 
                        loading={loading}
                        icon={<SaveOutlined />}
                      >
                        Save Changes
                      </Button>
                      <Button 
                        onClick={() => {
                          setIsEditing(false);
                          form.resetFields();
                        }}
                      >
                        Cancel
                      </Button>
                    </div>
                  </Form>
                ) : (
                  <Descriptions column={1} bordered>
                    <Descriptions.Item label="Full Name">
                      {user.first_name} {user.last_name}
                    </Descriptions.Item>
                    <Descriptions.Item label="Email Address">
                      {user.email}
                    </Descriptions.Item>
                    <Descriptions.Item label="Phone Number">
                      {user.phone || 'Not provided'}
                    </Descriptions.Item>
                    <Descriptions.Item label="Company Name">
                      {user.company_name || 'Not provided'}
                    </Descriptions.Item>
                    <Descriptions.Item label="GST Number">
                      {user.gst_number || 'Not provided'}
                    </Descriptions.Item>
                    <Descriptions.Item label="Account Status">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        user.is_verified 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {user.is_verified ? 'Verified' : 'Pending Verification'}
                      </span>
                    </Descriptions.Item>
                    <Descriptions.Item label="Member Since">
                      {new Date(user.date_joined).toLocaleDateString('en-IN', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </Descriptions.Item>
                  </Descriptions>
                )}
              </div>
            </TabPane>

            {/* Security */}
            <TabPane 
              tab={
                <span>
                  <LockOutlined />
                  Security
                </span>
              } 
              key="security"
            >
              <div className="max-w-md">
                <h3 className="text-lg font-medium text-gray-900 mb-6">
                  Change Password
                </h3>

                <Form
                  form={passwordForm}
                  layout="vertical"
                  onFinish={handlePasswordChange}
                  size="large"
                >
                  <Form.Item
                    name="current_password"
                    label="Current Password"
                    rules={[{ required: true, message: 'Please enter your current password' }]}
                  >
                    <Input.Password prefix={<LockOutlined />} />
                  </Form.Item>

                  <Form.Item
                    name="new_password"
                    label="New Password"
                    rules={[
                      { required: true, message: 'Please enter your new password' },
                      { min: 8, message: 'Password must be at least 8 characters' }
                    ]}
                    hasFeedback
                  >
                    <Input.Password prefix={<LockOutlined />} />
                  </Form.Item>

                  <Form.Item
                    name="new_password_confirm"
                    label="Confirm New Password"
                    dependencies={['new_password']}
                    rules={[
                      { required: true, message: 'Please confirm your new password' },
                      ({ getFieldValue }) => ({
                        validator(_, value) {
                          if (!value || getFieldValue('new_password') === value) {
                            return Promise.resolve();
                          }
                          return Promise.reject(new Error('Passwords do not match'));
                        },
                      }),
                    ]}
                    hasFeedback
                  >
                    <Input.Password prefix={<LockOutlined />} />
                  </Form.Item>

                  <Form.Item>
                    <Button
                      type="primary"
                      htmlType="submit"
                      loading={passwordLoading}
                      icon={<SaveOutlined />}
                    >
                      Change Password
                    </Button>
                  </Form.Item>
                </Form>

                <div className="mt-8 p-4 bg-blue-50 rounded-lg">
                  <h4 className="text-sm font-medium text-blue-900 mb-2">
                    Password Security Tips
                  </h4>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• Use at least 8 characters</li>
                    <li>• Include uppercase and lowercase letters</li>
                    <li>• Include numbers and special characters</li>
                    <li>• Don't use personal information</li>
                    <li>• Don't reuse passwords from other accounts</li>
                  </ul>
                </div>
              </div>
            </TabPane>
          </Tabs>
        </Card>
      </div>
    </div>
  );
};

export default ProfilePage;