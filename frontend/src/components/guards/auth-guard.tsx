import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/context/auth-context'
import { FullPageSpinner } from '@/components/ui/spinner'

interface AuthGuardProps {
  children: React.ReactNode
  allowedRoles?: string[]
}

export function AuthGuard({ children, allowedRoles }: AuthGuardProps) {
  const { user, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) return <FullPageSpinner />

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to={`/${user.role === 'vet' ? 'vet' : 'staff'}-dashboard`} replace />
  }

  return <>{children}</>
}

export function RoleRedirect() {
  const { user, isLoading } = useAuth()

  if (isLoading) return <FullPageSpinner />
  if (!user) return <Navigate to="/landing" replace />

  switch (user.role) {
    case 'vet':
      return <Navigate to="/vet-dashboard" replace />
    case 'staff':
    case 'admin':
      return <Navigate to="/staff-dashboard" replace />
    default:
      return <Navigate to="/landing" replace />
  }
}
