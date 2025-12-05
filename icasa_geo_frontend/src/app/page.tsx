'use client';

import MainLayout from '@/components/Layout/MainLayout';
import { FileText, FolderTree, Users, TrendingUp, Clock, CheckCircle } from 'lucide-react';

// Datos de ejemplo para el dashboard
const stats = [
  {
    name: 'Total Documentos',
    value: '156',
    change: '+12%',
    changeType: 'positive',
    icon: FileText,
  },
  {
    name: 'Pendientes Aprobación',
    value: '8',
    change: '-2',
    changeType: 'negative',
    icon: Clock,
  },
  {
    name: 'Categorías Activas',
    value: '24',
    change: '+3',
    changeType: 'positive',
    icon: FolderTree,
  },
  {
    name: 'Usuarios Activos',
    value: '45',
    change: '+5%',
    changeType: 'positive',
    icon: Users,
  },
];

const recentDocuments = [
  {
    id: 1,
    title: 'Política de Vacaciones',
    code: 'POL-001',
    category: 'Recursos Humanos',
    status: 'approved',
    updated: '2 horas',
  },
  {
    id: 2,
    title: 'Manual de Procedimientos IT',
    code: 'MAN-005',
    category: 'Tecnología',
    status: 'review',
    updated: '1 día',
  },
  {
    id: 3,
    title: 'Organigrama General',
    code: 'ORG-001',
    category: 'Estructura',
    status: 'draft',
    updated: '3 días',
  },
];

export default function Dashboard() {
  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-heading font-bold text-gray-900">
            Dashboard Ejecutivo
          </h1>
          <p className="text-gray-600">
            Resumen general del Sistema de Gestión Estratégica Organizacional
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <div key={stat.name} className="card-icasa">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 bg-icasa-50 rounded-lg flex items-center justify-center">
                      <Icon className="w-6 h-6 text-icasa-primary" />
                    </div>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                    <div className="flex items-baseline">
                      <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
                      <span className={`ml-2 text-sm font-medium ${
                        stat.changeType === 'positive' ? 'text-icasa-primary' : 'text-red-600'
                      }`}>
                        {stat.change}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Documents */}
          <div className="card-icasa">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-heading font-semibold text-gray-900">
                Documentos Recientes
              </h3>
              <button className="text-icasa-primary hover:text-icasa-dark text-sm font-medium">
                Ver todos
              </button>
            </div>
            <div className="space-y-3">
              {recentDocuments.map((doc) => (
                <div key={doc.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h4 className="text-sm font-medium text-gray-900">{doc.title}</h4>
                      <span className="text-xs text-gray-500">({doc.code})</span>
                    </div>
                    <p className="text-xs text-gray-600">{doc.category}</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`badge-${doc.status}`}>
                      {doc.status === 'approved' && 'Aprobado'}
                      {doc.status === 'review' && 'En Revisión'}
                      {doc.status === 'draft' && 'Borrador'}
                    </span>
                    <span className="text-xs text-gray-500">{doc.updated}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="card-icasa">
            <h3 className="text-lg font-heading font-semibold text-gray-900 mb-4">
              Acciones Rápidas
            </h3>
            <div className="space-y-3">
              <button className="w-full btn-icasa-primary text-left">
                <FileText className="w-4 h-4 inline mr-2" />
                Crear Nuevo Documento
              </button>
              <button className="w-full btn-icasa-secondary text-left">
                <FolderTree className="w-4 h-4 inline mr-2" />
                Agregar Categoría
              </button>
              <button className="w-full btn-icasa-outline text-left">
                <CheckCircle className="w-4 h-4 inline mr-2" />
                Revisar Pendientes
              </button>
            </div>
          </div>
        </div>

        {/* Activity Feed */}
        <div className="card-icasa">
          <h3 className="text-lg font-heading font-semibold text-gray-900 mb-4">
            Actividad Reciente
          </h3>
          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-icasa-primary rounded-full mt-2"></div>
              <div>
                <p className="text-sm text-gray-900">
                  <span className="font-medium">Juan Pérez</span> aprobó el documento 
                  <span className="font-medium"> "Política de Seguridad"</span>
                </p>
                <p className="text-xs text-gray-500">Hace 30 minutos</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
              <div>
                <p className="text-sm text-gray-900">
                  <span className="font-medium">María García</span> envió para revisión 
                  <span className="font-medium">"Manual de Calidad"</span>
                </p>
                <p className="text-xs text-gray-500">Hace 2 horas</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-icasa-light rounded-full mt-2"></div>
              <div>
                <p className="text-sm text-gray-900">
                  Nueva categoría <span className="font-medium">"Compliance"</span> creada
                </p>
                <p className="text-xs text-gray-500">Hace 1 día</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}