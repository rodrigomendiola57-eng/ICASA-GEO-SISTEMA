'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  Home, 
  BookOpen, 
  FolderTree, 
  Users, 
  Settings, 
  FileText,
  BarChart3,
  Search,
  Bell
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Base de Conocimiento', href: '/knowledge', icon: BookOpen },
  { name: 'Categorías', href: '/categories', icon: FolderTree },
  { name: 'Documentos', href: '/documents', icon: FileText },
  { name: 'Organigrama', href: '/organizational', icon: Users },
  { name: 'Reportes', href: '/reports', icon: BarChart3 },
  { name: 'Configuración', href: '/settings', icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <div className={`bg-white shadow-lg transition-all duration-300 ${isCollapsed ? 'w-16' : 'w-64'}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center">
          <div className="w-8 h-8 bg-icasa-primary rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">I</span>
          </div>
          {!isCollapsed && (
            <div className="ml-3">
              <h1 className="text-lg font-heading font-semibold text-icasa-dark">ICASA-GEO</h1>
              <p className="text-xs text-gray-500">Gestión Estratégica</p>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="mt-6 px-3">
        <div className="space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            
            return (
              <Link
                key={item.name}
                href={item.href}
                className={isActive ? 'sidebar-item-active' : 'sidebar-item'}
                title={isCollapsed ? item.name : undefined}
              >
                <Icon className="w-5 h-5 flex-shrink-0" />
                {!isCollapsed && (
                  <span className="ml-3 text-sm font-medium">{item.name}</span>
                )}
              </Link>
            );
          })}
        </div>
      </nav>

      {/* User Section */}
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
        <div className="flex items-center">
          <div className="w-8 h-8 bg-icasa-light rounded-full flex items-center justify-center">
            <span className="text-white font-medium text-sm">A</span>
          </div>
          {!isCollapsed && (
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-700">Admin</p>
              <p className="text-xs text-gray-500">Administrador</p>
            </div>
          )}
        </div>
      </div>

      {/* Collapse Button */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute top-20 -right-3 w-6 h-6 bg-icasa-primary rounded-full flex items-center justify-center text-white shadow-lg hover:bg-icasa-dark transition-colors"
      >
        <span className="text-xs">{isCollapsed ? '→' : '←'}</span>
      </button>
    </div>
  );
}