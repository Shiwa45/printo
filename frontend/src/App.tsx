// src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Import Ant Design CSS (v3)
import 'antd/dist/antd.css';
// Import our custom CSS
import './index.css';
// Import design editor styles
import './styles/design-editor.css';

// Context
import { AuthProvider } from './context/AuthContext';
import { CartProvider } from './context/CartContext';

// Components
import Layout from './components/common/Layout';

// Pages
import HomePage from './pages/Home/HomePage';
import LoginPage from './pages/Auth/LoginPage';
import RegisterPage from './pages/Auth/RegisterPage';
import AboutPage from './pages/About/AboutPage';
import ContactPage from './pages/Contact/ContactPage';
import ProductsPage from './pages/Products/ProductsPage';
import ProfilePage from './pages/Auth/ProfilePage';
import TemplatesPage from './pages/DesignEditor/TemplatesPage';
import EditorPage from './pages/DesignEditor/EditorPage';
import MyDesignsPage from './pages/DesignEditor/MyDesignsPage';
import CartPage from './pages/Cart/CartPage';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <CartProvider>
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/products" element={<ProductsPage />} />
              <Route path="/design/templates" element={<TemplatesPage />} />
              <Route path="/design/templates/:category" element={<TemplatesPage />} />
              <Route path="/design/editor/:productSlug" element={<EditorPage />} />
              <Route path="/design/editor/:category/:productSlug" element={<EditorPage />} />
              <Route path="/design/my-designs" element={<MyDesignsPage />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="/contact" element={<ContactPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/cart" element={<CartPage />} />
              <Route path="*" element={<div className="p-8 text-center">Page Not Found</div>} />
            </Routes>
          </Layout>
        </Router>
      </CartProvider>
    </AuthProvider>
  );
};

export default App;