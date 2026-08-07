import { type ReactNode } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/context/auth-context'
import {
  PawPrint,
  CalendarDays,
  ClipboardList,
  Package,
  LogOut,
  Menu,
  X,
  ChevronRight,
  Stethoscope,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar'
import { useState } from 'react'

interface NavItem {
  label: string
  href: string
  icon: ReactNode
}

const vetNav: NavItem[] = [
  { label: 'Patient Queue', href: '/vet-dashboard', icon: <ClipboardList size={18} /> },
]

const staffNav: NavItem[] = [
  { label: 'Dashboard', href: '/staff-dashboard', icon: <ClipboardList size={18} /> },
  { label: 'Calendar', href: '/staff-dashboard?tab=calendar', icon: <CalendarDays size={18} /> },
  { label: 'Inventory', href: '/staff-dashboard?tab=inventory', icon: <Package size={18} /> },
  { label: 'Check-In/Out', href: '/staff-dashboard?tab=checkin', icon: <Stethoscope size={18} /> },
]

export function AppLayout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const isVet = user?.role === 'vet'
  const navItems = isVet ? vetNav : staffNav

  const initials = user?.full_name
    ?.split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)

  return (
    <div className="flex h-screen overflow-hidden bg-muted/30">
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-30 flex flex-col border-r bg-sidebar-bg transition-all duration-300 lg:static',
          sidebarOpen ? 'w-64' : 'w-0 -translate-x-full lg:w-16 lg:translate-x-0',
        )}
      >
        <div className="flex h-16 items-center gap-2 border-b px-6">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
            <PawPrint className="h-5 w-5 text-primary-foreground" />
          </div>
          {sidebarOpen && (
            <span className="text-lg font-bold tracking-tight">Vetra</span>
          )}
        </div>

        <nav className="flex-1 space-y-1 p-3">
          {navItems.map((item) => {
            const isActive = location.pathname + location.search === item.href ||
              (location.pathname === item.href && !location.search) ||
              (item.href.includes('?') && location.search === item.href.split('?')[1])
            return (
              <button
                key={item.href}
                onClick={() => navigate(item.href)}
                className={cn(
                  'flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200 cursor-pointer',
                  isActive
                    ? 'bg-primary/10 text-primary'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                )}
              >
                {item.icon}
                {sidebarOpen && <span>{item.label}</span>}
                {!sidebarOpen && (
                  <div className="absolute left-14 z-50 hidden rounded-lg bg-popover px-3 py-2 text-sm shadow-md group-hover:block lg:group-hover:block">
                    {item.label}
                  </div>
                )}
              </button>
            )
          })}
        </nav>

        <div className="border-t p-3">
          <div className="flex items-center gap-3 rounded-lg px-3 py-2.5">
            <Avatar className="h-8 w-8">
              <AvatarImage src={user?.photo_url ?? undefined} alt={user?.full_name} />
              <AvatarFallback className="bg-primary/10 text-primary text-xs">
                {initials}
              </AvatarFallback>
            </Avatar>
            {sidebarOpen && (
              <div className="flex-1 text-left">
                <p className="text-sm font-medium leading-none">{user?.full_name}</p>
                <p className="mt-1 text-xs text-muted-foreground capitalize">{user?.role}</p>
              </div>
            )}
            <Button
              variant="ghost"
              size="icon"
              onClick={logout}
              className="ml-auto h-8 w-8 text-muted-foreground hover:text-destructive"
            >
              <LogOut size={16} />
            </Button>
          </div>
        </div>
      </aside>

      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex h-16 items-center gap-4 border-b bg-background px-6">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </Button>
          <div className="flex-1" />
        </header>

        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>

      {sidebarOpen && (
        <div
          className="fixed inset-0 z-20 bg-black/20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  )
}
