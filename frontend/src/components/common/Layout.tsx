// src/components/common/Layout.tsx
import React, { ReactNode } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Badge, Dropdown, Menu, Avatar } from 'antd';
import { 
  ShoppingCartOutlined, 
  UserOutlined, 
  LogoutOutlined,
  SettingOutlined,
  PlusOutlined,
  ClockCircleOutlined,
  MenuOutlined
} from '@ant-design/icons';
import { useAuth } from '../../context/AuthContext';
import { useCart } from '../../context/CartContext';

interface LayoutProps {
  children: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, isAuthenticated, logout } = useAuth();
  const { cart } = useCart();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  // User menu for authenticated users
  const userMenu = (
    <Menu>
      <Menu.Item key="profile">
        <Link to="/profile">My Profile</Link>
      </Menu.Item>
      <Menu.Item key="designs">
        <Link to="/design/my-designs">My Designs</Link>
      </Menu.Item>
      <Menu.Item key="orders">
        <Link to="/orders">Order History</Link>
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item key="settings">
        <Link to="/profile">Account Settings</Link>
      </Menu.Item>
      <Menu.Item key="logout" onClick={handleLogout}>
        Logout
      </Menu.Item>
    </Menu>
  );

  // Mobile menu
  const mobileMenu = (
    <Menu>
      <Menu.Item key="home">
        <Link to="/">Home</Link>
      </Menu.Item>
      <Menu.Item key="products">
        <Link to="/products">Products</Link>
      </Menu.Item>
      <Menu.Item key="design">
        <Link to="/design/templates">Design Tool</Link>
      </Menu.Item>
      <Menu.Item key="about">
        <Link to="/about">About</Link>
      </Menu.Item>
      <Menu.Item key="contact">
        <Link to="/contact">Contact</Link>
      </Menu.Item>
      {!isAuthenticated && (
        <>
          <Menu.Divider />
          <Menu.Item key="login">
            <Link to="/login">Login</Link>
          </Menu.Item>
          <Menu.Item key="register">
            <Link to="/register">Register</Link>
          </Menu.Item>
        </>
      )}
    </Menu>
  );

  const cartItemCount = cart?.items?.reduce((sum, item) => sum + item.quantity, 0) || 0;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center">
              <span className="text-xl font-bold text-primary-600">
                Drishthi Printing
              </span>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex space-x-8">
              <Link 
                to="/" 
                className="text-gray-700 hover:text-primary-600 transition-colors duration-200"
              >
                Home
              </Link>
              <Link 
                to="/products" 
                className="text-gray-700 hover:text-primary-600 transition-colors duration-200"
              >
                Products
              </Link>
              <Link 
                to="/design/templates" 
                className="text-gray-700 hover:text-primary-600 transition-colors duration-200"
              >
                Design Tool
              </Link>
              <Link 
                to="/about" 
                className="text-gray-700 hover:text-primary-600 transition-colors duration-200"
              >
                About
              </Link>
              <Link 
                to="/contact" 
                className="text-gray-700 hover:text-primary-600 transition-colors duration-200"
              >
                Contact
              </Link>
            </nav>

            {/* Right Section */}
            <div className="flex items-center space-x-4">
              {/* Shopping Cart */}
              {isAuthenticated && (
                <Link to="/cart" className="relative">
                  <Badge count={cartItemCount}>
                    <ShoppingCartOutlined 
                      className="text-xl text-gray-700 hover:text-primary-600 transition-colors duration-200" 
                    />
                  </Badge>
                </Link>
              )}

              {/* User Section */}
              {isAuthenticated ? (
                <Dropdown overlay={userMenu} placement="bottomRight" trigger={['click']}>
                  <div className="flex items-center space-x-2 cursor-pointer">
                    <Avatar 
                      size="small" 
                      src={user?.avatar}
                      className="bg-primary-500"
                    >
                      {!user?.avatar && <UserOutlined />}
                    </Avatar>
                    <span className="hidden sm:block text-gray-700 font-medium">
                      {user?.first_name || user?.email?.split('@')[0]}
                    </span>
                  </div>
                </Dropdown>
              ) : (
                <div className="hidden md:flex items-center space-x-4">
                  <Link 
                    to="/login" 
                    className="text-gray-700 hover:text-primary-600 transition-colors duration-200"
                  >
                    Login
                  </Link>
                  <Link 
                    to="/register" 
                    className="bg-primary-600 hover:bg-primary-700 text-white font-semibold px-4 py-2 rounded-lg transition-colors duration-200"
                  >
                    Register
                  </Link>
                </div>
              )}

              {/* Mobile Menu */}
              <div className="md:hidden">
                <Dropdown overlay={mobileMenu} placement="bottomRight" trigger={['click']}>
                  <MenuOutlined className="text-xl text-gray-700 cursor-pointer" />
                </Dropdown>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-12 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* Company Info */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Drishthi Printing</h3>
              <p className="text-gray-300 mb-4">
                Professional quality custom printing services with fast delivery and competitive prices.
              </p>
              <div className="text-gray-300 text-sm">
                <p>📍 Mumbai, India</p>
                <p>📞 +91 98765 43210</p>
                <p>✉️ info@drishthiprinting.com</p>
              </div>
            </div>

            {/* Quick Links */}
            <div>
              <h4 className="font-semibold mb-4">Quick Links</h4>
              <ul className="space-y-2 text-gray-300">
                <li><Link to="/products" className="hover:text-white">Products</Link></li>
                <li><Link to="/design/templates" className="hover:text-white">Design Tool</Link></li>
                <li><Link to="/about" className="hover:text-white">About Us</Link></li>
                <li><Link to="/contact" className="hover:text-white">Contact</Link></li>
              </ul>
            </div>

            {/* Services */}
            <div>
              <h4 className="font-semibold mb-4">Services</h4>
              <ul className="space-y-2 text-gray-300">
                <li><Link to="/products?category=business-cards" className="hover:text-white">Business Cards</Link></li>
                <li><Link to="/products?category=brochures" className="hover:text-white">Brochures</Link></li>
                <li><Link to="/products?category=flyers" className="hover:text-white">Flyers</Link></li>
                <li><Link to="/products?category=banners" className="hover:text-white">Banners</Link></li>
              </ul>
            </div>

            {/* Account */}
            <div>
              <h4 className="font-semibold mb-4">Account</h4>
              <ul className="space-y-2 text-gray-300">
                {isAuthenticated ? (
                  <>
                    <li><Link to="/profile" className="hover:text-white">My Profile</Link></li>
                    <li><Link to="/design/my-designs" className="hover:text-white">My Designs</Link></li>
                    <li><Link to="/orders" className="hover:text-white">Order History</Link></li>
                    <li><Link to="/cart" className="hover:text-white">Shopping Cart</Link></li>
                  </>
                ) : (
                  <>
                    <li><Link to="/login" className="hover:text-white">Login</Link></li>
                    <li><Link to="/register" className="hover:text-white">Register</Link></li>
                  </>
                )}
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Drishthi Printing. All rights reserved.</p>
            <div className="mt-2 space-x-4">
              <Link to="/privacy" className="hover:text-white">Privacy Policy</Link>
              <Link to="/terms" className="hover:text-white">Terms of Service</Link>
              <Link to="/support" className="hover:text-white">Support</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;