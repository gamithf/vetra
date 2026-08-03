import { useState, useEffect, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  Calendar, Package, AlertTriangle, CheckCircle2, Clock, Plus, Search,
  LogOut, Pill, Syringe, ShoppingCart, DollarSign, FileText,
  Loader2, PawPrint, UserCheck, Users, Ambulance,
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Spinner } from '@/components/ui/spinner'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import type { Appointment, InventoryItem, StaffDashboard } from '@/lib/api'
import { appointmentsApi, inventoryApi, dashboardApi } from '@/lib/api'
import { EmergencyIntakeModal } from '@/components/emergency-intake-modal'
import { CheckoutModal } from '@/components/checkout-modal'
import { useAuth } from '@/context/auth-context'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'

const statusConfig: Record<string, { label: string; variant: 'secondary' | 'default' | 'destructive' | 'outline' }> = {
  scheduled: { label: 'Scheduled', variant: 'secondary' },
  checked_in: { label: 'Checked In', variant: 'default' },
  in_progress: { label: 'In Progress', variant: 'default' },
  completed: { label: 'Completed', variant: 'outline' },
  cancelled: { label: 'Cancelled', variant: 'destructive' },
}

function formatDate(d: string, pattern: string): string {
  const date = new Date(d)
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  const dd = date.getDate()
  const mm = date.getMonth()
  const y = date.getFullYear()
  const h = date.getHours()
  const min = date.getMinutes().toString().padStart(2, '0')
  const h12 = h % 12 || 12
  const ampm = h >= 12 ? 'PM' : 'AM'
  // Longest/most-specific tokens must be replaced first so shorter
  // substrings (e.g. 'MMM d' inside 'MMMM d') don't corrupt the result.
  let out = pattern
  out = out.replace('EEEE, MMMM d, yyyy', `${days[date.getDay()]}, ${['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][mm]} ${dd}, ${y}`)
  out = out.replace('MMMM d, yyyy', `${['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][mm]} ${dd}, ${y}`)
  out = out.replace('MMMM d', `${['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][mm]} ${dd}`)
  out = out.replace('yyyy-MM-dd', `${y}-${(mm + 1).toString().padStart(2, '0')}-${dd.toString().padStart(2, '0')}`)
  out = out.replace('h:mm a', `${h12}:${min} ${ampm}`)
  out = out.replace('h:mm', `${h12}:${min}`)
  out = out.replace('MMM d', `${months[mm]} ${dd}`)
  return out
}

function CalendarView() {
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [loading, setLoading] = useState(true)
  useEffect(() => {
    appointmentsApi.list().then(setAppointments).catch(() => toast.error('Failed to load')).finally(() => setLoading(false))
  }, [])
  if (loading) return <Spinner className="py-20" />
  const grouped = appointments.reduce<Record<string, Appointment[]>>((acc, apt) => {
    const d = formatDate(apt.start_time, 'yyyy-MM-dd')
    if (!acc[d]) acc[d] = []
    acc[d].push(apt)
    return acc
  }, {})
  const sorted = Object.keys(grouped).sort()
  return (
    <div className="space-y-4">
      {sorted.length === 0 ? (
        <Card><CardContent className="py-16 text-center text-muted-foreground"><Calendar size={48} className="mx-auto mb-4 text-muted-foreground/30" />No appointments scheduled</CardContent></Card>
      ) : sorted.map((date) => (
        <Card key={date}>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base"><Calendar size={16} className="text-primary" />{formatDate(date, 'EEEE, MMMM d, yyyy')}</CardTitle>
            <CardDescription>{grouped[date].length} appointments</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {grouped[date].map((apt) => (
                <div key={apt.id} className={cn('flex items-center justify-between rounded-lg border p-3', apt.is_urgent && 'border-l-4 border-l-red-500')}>
                  <div className="flex items-center gap-4">
                    <div className="flex min-w-[60px] flex-col items-center">
                      <span className="text-sm font-bold">{formatDate(apt.start_time, 'h:mm')}</span>
                      <span className="text-xs text-muted-foreground">{formatDate(apt.start_time, 'h:mm a').split(' ')[1]}</span>
                    </div>
                    <div>
                      <p className="text-sm font-medium">#{apt.pet_id.slice(0, 8)}</p>
                      <p className="text-xs text-muted-foreground">{apt.reason || 'Check-up'}</p>
                    </div>
                  </div>
                  <Badge variant={statusConfig[apt.status]?.variant || 'secondary'}>{statusConfig[apt.status]?.label || apt.status}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

function InventoryView() {
  const [items, setItems] = useState<InventoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  useEffect(() => { inventoryApi.list().then(setItems).catch(() => toast.error('Failed to load inventory')).finally(() => setLoading(false)) }, [])
  const filtered = items.filter((i) => i.name.toLowerCase().includes(search.toLowerCase()) || i.category.toLowerCase().includes(search.toLowerCase()))
  const lowStock = filtered.filter((i) => i.is_low_stock)
  const normal = filtered.filter((i) => !i.is_low_stock)
  const catIcons: Record<string, React.ReactNode> = { medication: <Pill size={14} />, vaccine: <Syringe size={14} />, supply: <ShoppingCart size={14} />, food: <Package size={14} />, equipment: <Package size={14} /> }
  if (loading) return <Spinner className="py-20" />
  return (
    <div className="space-y-6">
      {lowStock.length > 0 && (
        <Card className="border-amber-200 bg-amber-50/50">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base text-amber-800"><AlertTriangle size={18} /> Low Stock ({lowStock.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {lowStock.map((item) => (
                <div key={item.id} className="flex items-center justify-between rounded-lg border border-amber-200 bg-white p-3">
                  <div><p className="text-sm font-medium">{item.name}</p><p className="text-xs text-muted-foreground">{item.quantity} / {item.min_quantity} {item.unit}</p></div>
                  <Badge variant="destructive" className="text-[10px]">{item.quantity} left</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
      <div className="relative">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
        <Input placeholder="Search inventory..." className="pl-9" value={search} onChange={(e) => setSearch(e.target.value)} />
      </div>
      <Table>
        <TableHeader>
          <TableRow><TableHead>Item</TableHead><TableHead>Category</TableHead><TableHead>Quantity</TableHead><TableHead>Min.</TableHead><TableHead>Status</TableHead></TableRow>
        </TableHeader>
        <TableBody>
          {normal.map((item) => (
            <TableRow key={item.id}>
              <TableCell className="font-medium">{item.name}</TableCell>
              <TableCell className="capitalize"><div className="flex items-center gap-2">{catIcons[item.category]}{item.category}</div></TableCell>
              <TableCell>{item.quantity} {item.unit}</TableCell>
              <TableCell>{item.min_quantity}</TableCell>
              <TableCell><Badge variant="outline" className="gap-1"><CheckCircle2 size={12} /> In Stock</Badge></TableCell>
            </TableRow>
          ))}
          {lowStock.map((item) => (
            <TableRow key={item.id} className="bg-red-50/30">
              <TableCell className="font-medium">{item.name}</TableCell>
              <TableCell className="capitalize"><div className="flex items-center gap-2">{catIcons[item.category]}{item.category}</div></TableCell>
              <TableCell className="font-bold text-red-600">{item.quantity} {item.unit}</TableCell>
              <TableCell>{item.min_quantity}</TableCell>
              <TableCell><Badge variant="destructive" className="gap-1"><AlertTriangle size={12} /> Low</Badge></TableCell>
            </TableRow>
          ))}
          {filtered.length === 0 && <TableRow><TableCell colSpan={5} className="py-10 text-center text-muted-foreground">No items found</TableCell></TableRow>}
        </TableBody>
      </Table>
    </div>
  )
}

export function StaffDashboard() {
  const [searchParams] = useSearchParams()
  const tab = searchParams.get('tab') || 'overview'
  const [dashData, setDashData] = useState<StaffDashboard>({ today_appointments: 0, low_stock_items: 0, pending_invoices: 0, checked_in_patients: 0 })
  const [loading, setLoading] = useState(true)
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [processing, setProcessing] = useState<string | null>(null)
  const [emergencyOpen, setEmergencyOpen] = useState(false)
  const [checkoutAppt, setCheckoutAppt] = useState<Appointment | null>(null)
  const [pendingCheckout, setPendingCheckout] = useState<Appointment[]>([])
  const { user } = useAuth()

  const load = useCallback(async () => {
    try {
      const [dash, apps, pending] = await Promise.all([
        dashboardApi.staff(),
        appointmentsApi.list({}),
        appointmentsApi.pendingCheckout(),
      ])
      setDashData(dash)
      setAppointments(apps)
      setPendingCheckout(pending)
    } catch { toast.error('Failed to load dashboard') }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { load() }, [load])

  const handleCheckIn = async (id: string) => {
    setProcessing(id)
    try { await appointmentsApi.checkIn(id); toast.success('Checked in'); load() }
    catch { toast.error('Check-in failed') }
    finally { setProcessing(null) }
  }

  const handleStart = async (id: string) => {
    setProcessing(id)
    try { await appointmentsApi.start(id); toast.success('Sent to vet'); load() }
    catch { toast.error('Failed') }
    finally { setProcessing(null) }
  }

  const setTab = (id: string) => {
    const p = new URLSearchParams(searchParams)
    p.set('tab', id)
    window.history.pushState(null, '', `?${p}`)
    window.dispatchEvent(new Event('popstate'))
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: <Clock size={16} /> },
    { id: 'calendar', label: 'Calendar', icon: <Calendar size={16} /> },
    { id: 'inventory', label: 'Inventory', icon: <Package size={16} /> },
    { id: 'checkin', label: 'Check-In / Out', icon: <UserCheck size={16} /> },
  ]

  if (loading) return <div className="flex min-h-[60vh] items-center justify-center"><Spinner size="lg" /></div>

  const activeApps = appointments.filter((a) => a.status !== 'cancelled' && a.status !== 'completed')

  return (
    <div className="animate-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Welcome, {user?.full_name?.split(' ')[0]}</h1>
          <p className="text-muted-foreground">Manage your clinic operations</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setEmergencyOpen(true)} variant="destructive" className="gap-2">
            <Ambulance size={16} /> Emergency
          </Button>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Today&apos;s Appts</CardTitle>
            <Calendar size={16} className="text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashData.today_appointments}</div>
            <p className="text-xs text-muted-foreground">scheduled today</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Checked In</CardTitle>
            <Users size={16} className="text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashData.checked_in_patients}</div>
            <p className="text-xs text-muted-foreground">currently waiting</p>
          </CardContent>
        </Card>
        <Card className={dashData.low_stock_items > 0 ? 'border-amber-200' : ''}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Low Stock</CardTitle>
            <Package size={16} className={dashData.low_stock_items > 0 ? 'text-amber-500' : 'text-muted-foreground'} />
          </CardHeader>
          <CardContent>
            <div className={cn('text-2xl font-bold', dashData.low_stock_items > 0 && 'text-amber-600')}>{dashData.low_stock_items}</div>
            <p className="text-xs text-muted-foreground">items need reorder</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Pending Invoices</CardTitle>
            <DollarSign size={16} className="text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashData.pending_invoices}</div>
            <p className="text-xs text-muted-foreground">awaiting payment</p>
          </CardContent>
        </Card>
      </div>

      <div className="flex flex-wrap gap-1 rounded-lg bg-muted p-1 w-fit">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={cn(
              'flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-all whitespace-nowrap',
              tab === t.id ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground',
            )}
          >{t.icon}{t.label}</button>
        ))}
      </div>

      {tab === 'overview' && (
        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader><CardTitle className="text-base">Quick Actions</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <Button variant="outline" className="h-12 w-full justify-start gap-3" onClick={() => setTab('checkin')}>
                <UserCheck size={16} className="text-primary" /> Check In a Patient
              </Button>
              <Button variant="outline" className="h-12 w-full justify-start gap-3" onClick={() => setTab('calendar')}>
                <Calendar size={16} className="text-primary" /> View Schedule
              </Button>
              <Button variant="outline" className="h-12 w-full justify-start gap-3" onClick={() => setTab('inventory')}>
                <Package size={16} className="text-primary" /> Check Inventory
              </Button>
              <Button variant="destructive" className="h-12 w-full justify-start gap-3" onClick={() => setEmergencyOpen(true)}>
                <Ambulance size={16} /> Emergency Intake
              </Button>
            </CardContent>
          </Card>
          <Card>
            <CardHeader><CardTitle className="text-base">Today&apos;s Overview</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">{dashData.today_appointments} appointments today, {dashData.checked_in_patients} checked in</p>
              {pendingCheckout.length > 0 && (
                <div className="rounded-lg border border-emerald-200 bg-emerald-50/50 p-3">
                  <div className="flex items-center gap-2 text-sm font-medium text-emerald-800">
                    <DollarSign size={16} /> {pendingCheckout.length} pending checkout{pendingCheckout.length > 1 ? 's' : ''}
                  </div>
                </div>
              )}
              <Button variant="outline" className="w-full gap-2" onClick={() => setTab('checkin')}>
                <UserCheck size={16} /> Go to Check-In
              </Button>
            </CardContent>
          </Card>
        </div>
      )}

      {tab === 'calendar' && <CalendarView />}
      {tab === 'inventory' && <InventoryView />}

      {tab === 'checkin' && (
        <div className="space-y-8">
          <div>
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold">Active Appointments</h3>
                <p className="text-sm text-muted-foreground">{activeApps.length} patients in queue</p>
              </div>
              <Button variant="outline" size="sm" onClick={load}>Refresh</Button>
            </div>
            {activeApps.length === 0 ? (
              <Card><CardContent className="flex flex-col items-center py-16"><CheckCircle2 size={48} className="mb-4 text-muted-foreground/30" /><p className="text-lg font-medium">All clear!</p><p className="text-sm text-muted-foreground">No patients waiting</p></CardContent></Card>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow><TableHead>Time</TableHead><TableHead>Patient</TableHead><TableHead>Reason</TableHead><TableHead>Status</TableHead><TableHead className="text-right">Action</TableHead></TableRow>
                </TableHeader>
                <TableBody>
                  {activeApps.map((apt) => (
                    <TableRow key={apt.id} className={cn(apt.is_urgent && 'bg-red-50/30')}>
                      <TableCell className="font-medium">{formatDate(apt.start_time, 'h:mm a')}</TableCell>
                      <TableCell><span className="font-medium">#{apt.pet_id.slice(0, 8)}</span></TableCell>
                      <TableCell className="text-muted-foreground capitalize">{apt.reason || 'Check-up'}</TableCell>
                      <TableCell>
                        <Badge variant={statusConfig[apt.status]?.variant || 'secondary'}>{statusConfig[apt.status]?.label || apt.status}</Badge>
                        {apt.is_urgent && <Badge variant="destructive" className="ml-1">URGENT</Badge>}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-2">
                          {apt.status === 'scheduled' && (
                            <Button size="sm" variant="outline" onClick={() => handleCheckIn(apt.id)} disabled={processing === apt.id} className="gap-1">
                              {processing === apt.id ? <Loader2 size={14} className="animate-spin" /> : <UserCheck size={14} />} Check In
                            </Button>
                          )}
                          {apt.status === 'checked_in' && (
                            <Button size="sm" onClick={() => handleStart(apt.id)} disabled={processing === apt.id} className="gap-1">
                              {processing === apt.id ? <Loader2 size={14} className="animate-spin" /> : <LogOut size={14} />} Send to Vet
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </div>

          <div>
            <h3 className="mb-4 text-lg font-semibold flex items-center gap-2">
              <DollarSign size={18} className="text-emerald-500" />
              Pending Checkout ({pendingCheckout.length})
            </h3>
            {pendingCheckout.length === 0 ? (
              <Card><CardContent className="flex flex-col items-center py-12"><DollarSign size={40} className="mb-3 text-muted-foreground/30" /><p className="font-medium">No pending checkouts</p><p className="text-sm text-muted-foreground">All completed appointments have been invoiced</p></CardContent></Card>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow><TableHead>Time</TableHead><TableHead>Patient</TableHead><TableHead>Reason</TableHead><TableHead className="text-right">Action</TableHead></TableRow>
                </TableHeader>
                <TableBody>
                  {pendingCheckout.map((apt) => (
                    <TableRow key={apt.id}>
                      <TableCell className="font-medium">{formatDate(apt.start_time, 'h:mm a')}</TableCell>
                      <TableCell><span className="font-medium">#{apt.pet_id.slice(0, 8)}</span></TableCell>
                      <TableCell className="text-muted-foreground">{apt.reason || 'Check-up'}</TableCell>
                      <TableCell className="text-right">
                        <Button size="sm" onClick={() => setCheckoutAppt(apt)} className="gap-1.5">
                          <DollarSign size={14} /> Checkout
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </div>
        </div>
      )}

      <EmergencyIntakeModal open={emergencyOpen} onClose={() => setEmergencyOpen(false)} onSuccess={load} />
      <CheckoutModal appointment={checkoutAppt} open={!!checkoutAppt} onClose={() => setCheckoutAppt(null)} onSuccess={load} />
    </div>
  )
}
