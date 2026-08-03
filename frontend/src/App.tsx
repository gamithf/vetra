import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'sonner'
import { AuthProvider } from '@/context/auth-context'
import { AuthGuard, RoleRedirect } from '@/components/guards/auth-guard'
import { AppLayout } from '@/components/layout/app-layout'
import { LandingPage } from '@/pages/landing'
import { LoginPage } from '@/pages/login'
import { RegisterPage } from '@/pages/register'
import { VetDashboard } from '@/pages/vet-dashboard'
import { StaffDashboard } from '@/pages/staff-dashboard'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/landing" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/" element={<RoleRedirect />} />
            <Route
              path="/vet-dashboard"
              element={
                <AuthGuard allowedRoles={['vet']}>
                  <AppLayout>
                    <VetDashboard />
                  </AppLayout>
                </AuthGuard>
              }
            />
            <Route
              path="/staff-dashboard"
              element={
                <AuthGuard allowedRoles={['staff', 'admin']}>
                  <AppLayout>
                    <StaffDashboard />
                  </AppLayout>
                </AuthGuard>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
          <Toaster
            position="top-right"
            richColors
            closeButton
            toastOptions={{
              duration: 4000,
            }}
          />
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
