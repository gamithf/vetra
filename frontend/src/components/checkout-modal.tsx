import { useState, useEffect } from 'react'
import { DollarSign, Loader2, X, CheckCircle2, CreditCard, Banknote, Landmark } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import type { Appointment, InvoiceWithItems } from '@/lib/api'
import { appointmentsApi, invoicesApi } from '@/lib/api'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'

interface Props {
  appointment: Appointment | null
  open: boolean
  onClose: () => void
  onSuccess: () => void
}

const paymentMethods = [
  { value: 'credit_card', label: 'Credit Card', icon: <CreditCard size={18} /> },
  { value: 'debit_card', label: 'Debit Card', icon: <CreditCard size={18} /> },
  { value: 'cash', label: 'Cash', icon: <Banknote size={18} /> },
  { value: 'bank_transfer', label: 'Bank Transfer', icon: <Landmark size={18} /> },
]

export function CheckoutModal({ appointment, open, onClose, onSuccess }: Props) {
  const [invoice, setInvoice] = useState<InvoiceWithItems | null>(null)
  const [loading, setLoading] = useState(false)
  const [paying, setPaying] = useState(false)
  const [paymentMethod, setPaymentMethod] = useState<string>('credit_card')

  useEffect(() => {
    if (open && appointment) {
      setLoading(true)
      setInvoice(null)
      setPaymentMethod('credit_card')
      appointmentsApi.createInvoice(appointment.id)
        .then(setInvoice)
        .catch(() => toast.error('Failed to create invoice'))
        .finally(() => setLoading(false))
    }
  }, [open, appointment])

  const handlePay = async () => {
    if (!invoice) return
    setPaying(true)
    try {
      await invoicesApi.pay(invoice.id, { payment_method: paymentMethod })
      toast.success('Payment processed successfully!')
      onSuccess()
      onClose()
    } catch {
      toast.error('Payment failed')
    } finally {
      setPaying(false)
    }
  }

  if (!open || !appointment) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <Card className="w-full max-w-lg animate-in shadow-2xl">
        <CardHeader className="flex flex-row items-center justify-between pb-3">
          <CardTitle className="flex items-center gap-2 text-lg">
            <DollarSign size={20} className="text-emerald-500" />
            Checkout
          </CardTitle>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X size={18} />
          </Button>
        </CardHeader>
        <CardContent className="space-y-5">
          <div className="flex items-center gap-3 rounded-lg bg-muted/50 p-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary font-bold uppercase">
              #{appointment.pet_id.slice(0, 2)}
            </div>
            <div>
              <p className="text-sm font-medium">Patient #{appointment.pet_id.slice(0, 8)}</p>
              <p className="text-xs text-muted-foreground">{appointment.reason || 'Check-up'}</p>
            </div>
            <Badge variant="success" className="ml-auto">Completed</Badge>
          </div>

          {loading ? (
            <div className="flex justify-center py-10">
              <Loader2 size={24} className="animate-spin text-primary" />
            </div>
          ) : invoice ? (
            <>
              <div className="space-y-2">
                <p className="text-sm font-medium">Invoice Items</p>
                <div className="rounded-lg border divide-y">
                  {invoice.items.map((item) => (
                    <div key={item.id} className="flex items-center justify-between px-4 py-2.5 text-sm">
                      <span>{item.description}</span>
                      <span className="font-medium tabular-nums">
                        {item.quantity > 1 && `${item.quantity} × `}${item.unit_price.toFixed(2)}
                      </span>
                    </div>
                  ))}
                  <div className="flex items-center justify-between bg-muted/30 px-4 py-3 text-sm font-bold">
                    <span>Total</span>
                    <span>${invoice.total_amount.toFixed(2)}</span>
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <p className="text-sm font-medium">Payment Method</p>
                <div className="grid grid-cols-2 gap-2">
                  {paymentMethods.map((pm) => (
                    <button
                      key={pm.value}
                      onClick={() => setPaymentMethod(pm.value)}
                      className={cn(
                        'flex items-center gap-2 rounded-lg border-2 p-3 text-sm transition-all',
                        paymentMethod === pm.value
                          ? 'border-primary bg-primary/5'
                          : 'border-input hover:border-muted-foreground/30',
                      )}
                    >
                      {pm.icon}
                      {pm.label}
                      {paymentMethod === pm.value && <CheckCircle2 size={14} className="ml-auto text-primary" />}
                    </button>
                  ))}
                </div>
              </div>

              <Button className="w-full h-11 gap-2" onClick={handlePay} disabled={paying}>
                {paying ? (
                  <><Loader2 size={16} className="animate-spin" /> Processing...</>
                ) : (
                  <><DollarSign size={16} /> Pay ${invoice.total_amount.toFixed(2)}</>
                )}
              </Button>
            </>
          ) : (
            <p className="py-8 text-center text-sm text-muted-foreground">Failed to load invoice</p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
