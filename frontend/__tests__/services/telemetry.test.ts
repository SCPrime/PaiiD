import { telemetry } from '../../services/telemetry'

describe('TelemetryService', () => {
  beforeEach(() => {
    telemetry.enable()  // Enable telemetry for tests
    telemetry.clear()
  })

  test('tracks events', () => {
    telemetry.track({
      userId: 'test-user',
      userRole: 'beta',
      component: 'TestComponent',
      action: 'test_action',
      metadata: { test: true },
    })

    const events = telemetry.exportEvents()
    expect(events).toHaveLength(1)
    expect(events[0].action).toBe('test_action')
  })

  test('tracks page views', () => {
    telemetry.trackPageView('user-1', 'alpha', 'Dashboard')

    const events = telemetry.exportEvents()
    expect(events).toHaveLength(1)
    expect(events[0].action).toBe('page_view')
  })

  test('tracks clicks', () => {
    telemetry.trackClick('user-1', 'beta', 'Button', 'submit-btn')

    const events = telemetry.exportEvents()
    expect(events).toHaveLength(1)
    expect(events[0].action).toBe('button_click')
    expect(events[0].metadata?.buttonName).toBe('submit-btn')
  })

  test('tracks errors', () => {
    const error = new Error('Test error')
    telemetry.trackError('user-1', 'owner', 'ErrorBoundary', error)

    const events = telemetry.exportEvents()
    expect(events).toHaveLength(1)
    expect(events[0].action).toBe('error')
    expect(events[0].metadata?.message).toBe('Test error')
  })

  test('tracks form submissions', () => {
    telemetry.trackFormSubmit('user-1', 'beta', 'TradeForm', { formId: 'trade-form', success: true, symbol: 'AAPL' })

    const events = telemetry.exportEvents()
    expect(events).toHaveLength(1)
    expect(events[0].action).toBe('form_submit')
    expect(events[0].metadata?.success).toBe(true)
  })

  test('clears events', () => {
    telemetry.track({
      userId: 'test-user',
      userRole: 'beta',
      component: 'TestComponent',
      action: 'test_action',
    })

    expect(telemetry.exportEvents()).toHaveLength(1)

    telemetry.clear()

    expect(telemetry.exportEvents()).toHaveLength(0)
  })
})
