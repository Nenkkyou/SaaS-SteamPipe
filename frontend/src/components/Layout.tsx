import React, { useEffect, useState, ReactNode } from 'react';
import axios from 'axios';

interface BrandingConfig {
  logo_url?: string;
  primary_color?: string;
  brand_name?: string;
  subdomain?: string;
  theme_class?: string;
}

interface Branding {
  nome: string;
  config: BrandingConfig;
}

interface LayoutProps {
  children: ReactNode;
}

const defaultBranding: BrandingConfig = {
  logo_url: 'https://images.pexels.com/photos/3184291/pexels-photo-3184291.jpeg',
  primary_color: '#0ea5e9',
  brand_name: 'Default Brand',
  theme_class: 'bg-white text-gray-900',
};

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [branding, setBranding] = useState<BrandingConfig>(defaultBranding);

  useEffect(() => {
    const fetchBranding = async () => {
      try {
        const response = await axios.get('/api/v1/branding/');
        if (response.data && response.data.config) {
          setBranding({
            ...defaultBranding,
            ...response.data.config,
          });
        }
      } catch (error) {
        console.error('Failed to fetch branding:', error);
      }
    };
    fetchBranding();
  }, []);

  return (
    <div className={branding.theme_class || defaultBranding.theme_class} style={{ minHeight: '100vh' }}>
      <header className="flex items-center p-4 shadow-md" style={{ backgroundColor: branding.primary_color || defaultBranding.primary_color }}>
        <img src={branding.logo_url || defaultBranding.logo_url} alt="Logo" className="h-10 w-10 object-contain" />
        <h1 className="ml-4 text-white text-xl font-semibold">{branding.brand_name || defaultBranding.brand_name}</h1>
      </header>
      <main className="p-6">
        {children}
      </main>
    </div>
  );
};

export default Layout;
